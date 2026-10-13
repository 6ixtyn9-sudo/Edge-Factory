"""The enhancement lane: hit-rate floor gate, plus autobets' lifecycle on its own state.

Operator rulings, 2026-10-12, which this file pins:

* "betting on ev will lead us to not bet at all, we have the track record of
  enhanced, we know what wins more, we just need prices above a certain
  threshold, like how autobets does it." — the gate is a per-market minimum
  price derived from the settled registry (``ENHANCEMENT_PRICE_FLOORS``). There
  is NO EV veto: ``enhancement_breakeven`` / ``enhancement_edge_sample`` stay on
  the row as information and gate nothing.
* "i need it to look like how autobets presents it and to have the same
  lifecycle of autobets" and "i dont want them to change the system have now …
  additional" — the lane reuses the shared freeze / settle / bank / take-profit
  lifecycle and keeps its own state file and artifact. Nothing in the main
  lane's behaviour changes.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory import enh_registry as reg  # noqa: E402

DAY = "2026-10-12"


def _pick(home="Pyunik Yerevan", away="BKMA", market="match_over_25", *,
          price=1.72, bucket="CERTIFIED_CLEAN", rule="r1", prob=0.46,
          label="Match Over 2.5 Goals", book="Stake.com"):
    return {"home": home, "away": away, "match": f"{home} vs {away}", "date": DAY,
            "bucket": bucket, "rule": rule, "recommended_enhancement": market,
            "enhancement_label": label, "enhancement_probability": prob,
            "enhancement_price": price, "enhancement_price_book": book,
            "enhancement_price_source": "oddspapi"}


class _PinnedDatetime(datetime):
    """``datetime`` whose ``now()`` is fixed to the test's DAY, 08:00 local.

    The lane's target day is "today" on the wall clock (``cmd_enhancement``
    reads ``datetime.now(TZ)``), while every fixture in this file is written for
    ``DAY``. Left on the real clock the tests passed only on the day DAY was
    today and failed on every later run. Pinning the clock to DAY keeps the
    fixtures and the run on the same day, and 08:00 keeps the default run before
    the 09:00 freeze, so the draft/freeze tests still exercise both branches.
    """

    @classmethod
    def now(cls, tz=None):
        pinned = datetime.fromisoformat(f"{DAY}T08:00:00").replace(tzinfo=at.TZ)
        return pinned if tz is None else pinned.astimezone(tz)


@pytest.fixture(autouse=True)
def _tmp_lane(tmp_path, monkeypatch):
    """Every test writes lane state and the artifact into a temp dir."""
    monkeypatch.setattr(at, "datetime", _PinnedDatetime)
    localdata = tmp_path / "localdata"
    localdata.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(at, "LOCALDATA", localdata)
    monkeypatch.setattr(at, "ENHANCEMENT_LANE", at.Lane(
        localdata / "enhancement_tickets_state.json", "enhancement_tickets",
        "ENHANCEMENT TICKETS (ROLLING)", at.STAKE_FRAC))
    # Main-lane paths must never be touched by these tests either.
    monkeypatch.setattr(at, "STATE_FILE", localdata / "auto_tickets_state.json")
    # The board renders floors from ITS module's localdata (the same constant the
    # picks come from): point it at the same temp root so the board and the lane
    # read one registry, and drop the render cache.
    import picks_today as pt
    monkeypatch.setattr(pt, "LOCALDATA", localdata)
    pt._ENH_FLOORS_CACHE.clear()
    monkeypatch.setenv(at.ENH_BOARD_FLAG, "1")
    yield localdata


def _board(localdata: Path, picks: list[dict]) -> None:
    (localdata / "picks_today.json").write_text(json.dumps(picks))


def _registry(localdata: Path) -> None:
    """A registry with one settled record of each provenance shape."""
    (localdata / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {"match_over_25@v1": {
            "status": "PAPER", "n": 2, "hits": 1, "profit": 0.5,
            "inv_price_sum": 1.1, "multi_n": 0, "processed": [],
            "records": [
                # legacy record: no slice provenance at all
                {"date": DAY, "match": "A vs B", "price": 1.9, "hit": True,
                 "source": "oddspapi", "multi_source": False},
                {"date": DAY, "match": "C vs D", "price": 1.7, "hit": False,
                 "source": "oddspapi", "multi_source": False,
                 "bucket": "SKIPPED_VETO", "rule": "ml-meta avg_p>=55", "stated": 0.4},
            ]}}}), encoding="utf-8")


# --------------------------------------------------------------------------
# the gate: floor in, EV out
# --------------------------------------------------------------------------

def test_at_or_above_the_floor_fires_and_below_it_does_not():
    assert reg.floor_for("match_over_25") == 1.60
    assert reg.clears_floor("match_over_25", 1.60) is True
    assert reg.clears_floor("match_over_25", 1.59) is False
    # every market's floor is its own, at the stated literal
    assert reg.clears_floor("match_over_15", 1.45) is True
    assert reg.clears_floor("match_over_35", 3.30) is True
    assert reg.clears_floor("btts_yes", 1.85) is True
    assert reg.clears_floor("match_over_35", 3.29) is False


def test_a_market_with_no_settled_evidence_has_no_floor_and_does_not_fire():
    assert reg.floor_for("away_under_35") is None
    assert reg.clears_floor("away_under_35", 1.90) is False
    assert reg.clears_floor(None, 1.90) is False
    # junk prices are never "above the floor" (RT-2)
    for junk in (None, "1.9", float("nan"), float("inf"), 1.0, 0.9, True):
        assert reg.clears_floor("match_over_25", junk) is False


def test_ev_fields_gate_nothing(tmp_path, _tmp_lane):
    """A big sample edge below the floor is still no bet — there is no EV veto."""
    above = _pick(price=1.72)
    below = _pick(price=1.59, prob=0.95)          # huge sample edge, under floor
    legs = {l["price"]: l for l in at.enhancement_legs([above, below])}
    assert legs[1.72]["verdict"] == "fire"
    assert legs[1.59]["verdict"] == "below_floor"
    # The information fields remain on the row; nothing consults them here.
    assert below.get("enhancement_edge_sample") is None  # set by enh_pricing, not here


def test_unpriced_and_unpriceable_legs_do_not_fire():
    unpriced = _pick(market="match_over_35", price=None)
    unpriceable = _pick(market="home_under_35", price=None)
    legs = {l["market"]: l for l in at.enhancement_legs([unpriced, unpriceable])}
    assert legs["match_over_35"]["verdict"] == "unpriced"
    assert legs["home_under_35"]["verdict"] == "unpriceable"
    assert not any(l["verdict"] == "fire" for l in legs.values())


def test_a_missing_or_junk_price_never_fires():
    for price in (None, 1.0, float("nan"), "1.72"):
        legs = at.enhancement_legs([_pick(price=price)])
        assert legs[0]["verdict"] != "fire"


# --------------------------------------------------------------------------
# presentation: 2-leg accas, the main lane's card, the lane's own evidence
# --------------------------------------------------------------------------

def _now():
    import datetime as _dt
    return _dt.datetime.now(at.TZ)


def _distinct(n, market="match_over_25", price=1.90, **kw):
    """`n` firing picks on `n` DIFFERENT fixtures.

    Distinct on purpose: the same-fixture guard is itself a gate, and a test
    that is not about it must not trip it by accident. Prices descend with
    rank so the order — and therefore the barbell pairing — is the list order.
    """
    fixtures = [("Alpha FC", "Beta FC"), ("Gamma FC", "Delta FC"),
                ("Epsilon FC", "Zeta FC"), ("Eta FC", "Theta FC"),
                ("Iota FC", "Kappa FC"), ("Lambda FC", "Mu FC")]
    return [_pick(home=h, away=a, market=market, price=price - 0.01 * i, **kw)
            for i, (h, a) in enumerate(fixtures[:n])]


def _legs_and_plan(localdata, bank_eff=100.0, fixture_report=None):
    legs = at.enhancement_legs(json.loads((localdata / "picks_today.json").read_text()))
    report = {} if fixture_report is None else fixture_report
    pool = at.enhancement_pool(legs)
    plan = at.plan_day(pool, bank_eff, stake_frac=at.ENHANCEMENT_LANE.stake_frac,
                       fixture_report=report)
    at._carry_lane_evidence(plan, pool)      # what cmd_enhancement does
    return legs, plan


def test_the_card_is_two_leg_accas_barbelled_at_the_main_lanes_stake(tmp_path, _tmp_lane):
    """§1: accas exactly the way autobets does them — pairing, size, stakes."""
    _registry(_tmp_lane)
    _board(_tmp_lane, _distinct(4))
    legs, plan = _legs_and_plan(_tmp_lane)
    assert [l["verdict"] for l in legs] == ["fire"] * 4
    # barbell: strongest with weakest — 1st+4th, then 2nd+3rd
    assert [[l["match"] for l in a["legs"]] for a in plan] == [
        ["Alpha FC vs Beta FC", "Eta FC vs Theta FC"],
        ["Gamma FC vs Delta FC", "Epsilon FC vs Zeta FC"]]
    for a in plan:
        assert a["odds"] == pytest.approx(
            round(a["legs"][0]["odds"] * a["legs"][1]["odds"], 2))
    # the main lane's arithmetic, on the LANE's stake knob: 25% / MAX_ACCAS
    assert [a["stake_pct"] for a in plan] == pytest.approx([12.5, 12.5])
    assert sum(a["stake_pct"] for a in plan) == pytest.approx(
        at.ENHANCEMENT_LANE.stake_frac * 100.0)
    # ...and identical to what the MAIN lane's own call would size for the
    # same pool (B-6: the two arithmetic paths cannot disagree)
    main_plan = at.plan_day(at.enhancement_pool(legs), 100.0)
    assert [a["stake_pct"] for a in plan] == [a["stake_pct"] for a in main_plan]
    assert [[l["match"] for l in a["legs"]] for a in plan] == \
           [[l["match"] for l in a["legs"]] for a in main_plan]

    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0, root=tmp_path)
    assert txt.count("[ACCA #1]") == 1 and txt.count("[ACCA #2]") == 1
    assert "[ENH #" not in txt
    assert txt.count("— stake 12.5% of capital (12.5% of free bank)") == 2
    # per-leg evidence: stated %, the market's registry line, its floor, the book
    assert "(stated 46%)" in txt
    assert "[registry 50% n=2 · floor 1.60 (inherited) · Stake.com]" in txt
    assert "deploying 25% of free bank today = 25.0% of capital" in txt


def test_a_lone_eligible_leg_is_a_no_bet_that_says_so(tmp_path, _tmp_lane):
    """§3/§5(3): below MIN_ACCAS the card prints its reason, never a single."""
    _board(_tmp_lane, _distinct(1))
    legs, plan = _legs_and_plan(_tmp_lane)
    assert plan == []
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    assert "NO BET — only 1 eligible leg(s), need 2 for an acca" in txt
    assert "(bank stays unbet; a lone leg is never a single)" in txt
    assert "[ACCA #" not in txt and "[ENH #" not in txt and "deploying" not in txt


def test_three_eligible_legs_drop_the_leftover_never_a_single(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(3))
    legs, plan = _legs_and_plan(_tmp_lane)
    assert len(plan) == 1 and len(plan[0]["legs"]) == 2
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    assert "[ACCA #1]" in txt and "[ACCA #2]" not in txt
    assert "1 eligible leg(s) left over without an acca partner (never a single)" in txt


def test_a_same_fixture_duplicate_is_dropped_and_reported(tmp_path, _tmp_lane):
    """B-1's eligibility: priced, clearing its floor, and not a fixture dupe."""
    _board(_tmp_lane, [
        _pick(market="match_over_25", price=1.90, prob=0.40),
        _pick(market="btts_yes", price=1.90, prob=0.60,
              label="Both Teams to Score - Yes (BTTS-Yes)")])
    report = {}
    legs, plan = _legs_and_plan(_tmp_lane, fixture_report=report)
    pool = at.enhancement_pool(legs)
    kept, dropped = at.dedup_fixture_legs(at.rank_legs(pool))
    # the HIGHEST-RANKED leg of the pair survives — the btts leg here
    assert [l["market"] for l in kept] == ["btts_yes"]
    assert [l["market"] for l in dropped] == ["match_over_25"]
    assert report["dropped"] == ["Pyunik Yerevan vs BKMA"]
    assert plan == []                     # one survivor is not a card
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0, fixture_report=report)
    assert ("same-fixture duplicate(s) dropped (one fixture rides a card once): "
            "Pyunik Yerevan vs BKMA") in txt
    assert "NO BET — only 1 eligible leg(s), need 2 for an acca" in txt


def test_a_vetoed_parent_stays_shadow(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(2, bucket="SKIPPED_VETO"))
    legs, plan = _legs_and_plan(_tmp_lane)
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    acca_line = next(l for l in txt.splitlines() if l.startswith("[ACCA #1]"))
    assert acca_line.endswith(at.ENH_SHADOW_TAG)
    assert "[SHADOW — paper]" in txt


def test_the_artifact_matches_autobets_conventions(tmp_path, _tmp_lane):
    _registry(_tmp_lane)
    _board(_tmp_lane, _distinct(2) + [
        _pick(home="Nu FC", away="Xi FC", price=1.59)])       # below floor
    legs, plan = _legs_and_plan(_tmp_lane)
    txt = at.render_enhancement_tickets(
        at.fresh_state(), DAY, legs, plan, _now(),
        should_freeze=True, freeze_record={"frozen_at": f"{DAY}T09:00:00+02:00"},
        bank_eff=100.0)
    lines = txt.splitlines()
    assert lines[0] == f"ENHANCEMENT TICKETS (ROLLING) — {DAY}"
    assert set(lines[1]) == {"="} and len(lines[1]) == 62
    assert lines[2].startswith("PERFORMANCE: total bank 100.0% of capital (x1.00) = ")
    assert "next take-profit notification at 200.0%" in lines[2]
    assert "ENHANCEMENT SLICE (settled, registry)" in txt
    assert "by bucket" in txt and "by rule" in txt
    # the refused leg is visible for audit but is NOT an instruction
    assert "[NO BET]" in txt and "below floor 1.60 [inherited] — no bet" in txt
    assert "Nu FC" not in "\n".join(
        l for l in txt.splitlines() if l.startswith("[ACCA #"))
    assert "deploying 25% of free bank today" in txt
    assert "+100% per cycle (performance-based; you act on it)" in txt
    assert "All figures are percentages of capital." in txt
    assert lines[-1] == "FROZEN AT 09:00 - FINAL"
    # percentages only — no currency anywhere in the artifact
    assert "$" not in txt and "ZAR" not in txt and "R " not in txt


def test_slices_report_legacy_records_as_unattributed(tmp_path, _tmp_lane):
    _registry(_tmp_lane)
    by_bucket = reg.slice_for_market(_tmp_lane.parent, "match_over_25", "bucket")
    assert by_bucket[reg.UNATTRIBUTED]["n"] == 1          # the pre-provenance record
    assert by_bucket["SKIPPED_VETO"]["n"] == 1            # the attributed one
    by_rule = reg.slice_for_market(_tmp_lane.parent, "match_over_25", "rule")
    assert by_rule["ml-meta avg_p>=55"]["n"] == 1


def test_registry_track_record_carries_the_floor_next_to_the_rate(tmp_path, _tmp_lane):
    _registry(_tmp_lane)
    row = [r for r in reg.market_track_record(_tmp_lane.parent) if r["market"] == "match_over_25"][0]
    assert (row["n"], row["hits"], row["rate"]) == (2, 1, 0.5)
    assert row["breakeven"] == pytest.approx(2.0)         # 1 / rate
    assert row["floor"] == 1.60                           # the literal, not a guess


# --------------------------------------------------------------------------
# lifecycle: freeze write-once, own state, flag off = nothing happens
# --------------------------------------------------------------------------

def _args(**kw):
    import types
    base = dict(date=None, force=False, settle=False, today=False, status=False)
    base.update(kw)
    return types.SimpleNamespace(**base)


def _scores_for(pairs, day=DAY):
    """{key: (hs, gs)} in the settled-facts key space, from (home, away, hs, gs)."""
    out = {}
    for home, away, hs, gs in pairs:
        for hk, ak in at._result_write_keys(home, away):
            out[(day, hk, ak)] = (hs, gs)
    return out


def _freeze_now(localdata):
    """Run the lane command as the 09:00 run does; return the loaded state."""
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 0)
    try:
        st = at.fresh_state()
        at.cmd_enhancement(_args(), st)
    finally:
        monkey.undo()
    return json.loads((localdata / "enhancement_tickets_state.json").read_text())


def test_the_freeze_is_write_once_and_force_cannot_rewrite_it(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(2))
    path = _tmp_lane / "enhancement_tickets_state.json"
    art = _tmp_lane / f"enhancement_tickets_{DAY}.txt"
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 0)                  # past the 09:00 boundary
    try:
        st = at.fresh_state()
        at.cmd_enhancement(_args(), st)
        frozen_text = art.read_text()
        stamp = json.loads(path.read_text())["frozen_by_date"][DAY]
        assert stamp["final"] is True

        # A later run with a DIFFERENT card must not move a frozen date...
        _board(_tmp_lane, _distinct(2, market="btts_yes", price=2.10))
        at.cmd_enhancement(_args(), json.loads(path.read_text()))
        assert art.read_text() == frozen_text
        # ...and neither may --force (that is how bets rotate under the operator).
        at.cmd_enhancement(_args(force=True), json.loads(path.read_text()))
        assert art.read_text() == frozen_text
        assert json.loads(path.read_text())["frozen_by_date"][DAY] == stamp
    finally:
        monkey.undo()


def test_before_the_freeze_hour_the_card_is_a_draft(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(2))
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 25)                 # never reached
    try:
        at.cmd_enhancement(_args(), at.fresh_state())
    finally:
        monkey.undo()
    state = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())
    assert not state.get("frozen_by_date")
    # a draft is already the acca shape, so --status and settle read it
    assert [s["date"] for s in state["open_slips"]] == [DAY]
    assert (at.ENHANCEMENT_LANE.state_file).exists()
    assert (_tmp_lane / f"enhancement_tickets_{DAY}.txt").exists()


def test_the_lane_keeps_its_own_state_and_the_main_state_file_alone(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(2))
    _freeze_now(_tmp_lane)
    assert (at.ENHANCEMENT_LANE.state_file).exists()
    assert at.ENHANCEMENT_LANE.state_file.name == "enhancement_tickets_state.json"
    assert not (tmp_path / "localdata" / "auto_tickets_state.json").exists()


def test_the_frozen_entry_has_the_main_lanes_shape_and_nothing_else(tmp_path, _tmp_lane):
    """§5(1)/(2): 'keys identical to main lane', pinned against the main lane."""
    _board(_tmp_lane, _distinct(2))
    state = _freeze_now(_tmp_lane)
    lane_entry = state["open_slips"][0]
    # the main lane's own writer, on a main-lane pool (no lane fields at all)
    main_pool = [{"match": "Alpha FC vs Beta FC", "pick": "home",
                  "prob": 0.46, "odds": 1.90},
                 {"match": "Gamma FC vs Delta FC", "pick": "away",
                  "prob": 0.46, "odds": 1.89}]
    main_state = at.fresh_state()
    at.upsert_slip(main_state, DAY, at.plan_day(main_pool, 100.0))
    main_entry = main_state["open_slips"][0]
    # 'keys identical to the main lane' — pinned against the main lane itself
    assert set(lane_entry) == set(main_entry)
    assert {"date", "accas", "staked_pct"} <= set(main_entry)
    assert set(lane_entry["accas"][0]) == set(main_entry["accas"][0])
    assert {"legs", "odds", "stake_pct"} <= set(main_entry["accas"][0])
    assert lane_entry["staked_pct"] == main_entry["staked_pct"]
    lane_leg = lane_entry["accas"][0]["legs"][0]
    main_leg = main_entry["accas"][0]["legs"][0]
    # the card leg carries every key the main lane's leg carries, then its own
    assert set(main_leg) <= set(lane_leg)
    assert {"match", "pick", "prob", "odds", "result"} <= set(main_leg)
    assert {"market", "label", "floor", "price_book", "shadow"} <= set(lane_leg)
    assert "market" not in main_leg and "shadow" not in main_leg
    assert lane_leg["fixture_key"][0] == DAY


def test_the_market_grading_path_is_the_registrys_own_hit_definition():
    """The frozen leg's market is graded by the definition the registry uses."""
    cases = [("match_over_25", "over", 3, 0), ("match_over_25", "over", 1, 0),
             ("match_over_35", "over", 4, 0), ("btts_yes", "yes", 2, 1),
             ("btts_yes", "yes", 3, 0), ("match_under_25", "under", 2, 1)]
    for market, selection, hs, gs in cases:
        leg = {"market": market, "pick": selection, "match": "Alpha FC vs Beta FC",
               "fixture_key": [DAY, "Alpha FC", "Beta FC"]}
        got = at.enhancement_leg_result(leg, DAY, _scores_for([("Alpha FC", "Beta FC", hs, gs)]))
        want = reg.check_enhancement_hit(market, selection, hs, gs)
        assert got == ("win" if want else "loss"), (market, hs, gs)
    # a market the scorer has no rule for is HELD, never graded
    leg = {"market": "no_such_market", "pick": "over", "match": "Alpha FC vs Beta FC",
           "fixture_key": [DAY, "Alpha FC", "Beta FC"]}
    assert at.enhancement_leg_result(leg, DAY, _scores_for([("Alpha FC", "Beta FC", 3, 0)])) is None
    # and no score at all is 'not known yet', not a loss
    assert at.enhancement_leg_result(leg, DAY, {}) is None


def test_a_market_leg_on_a_conflicted_fixture_is_held_as_a_conflict():
    leg = {"market": "match_over_25", "pick": "over", "match": "Pafos vs Dinamo Tirana",
           "fixture_key": [DAY, "Pafos", "Dinamo Tirana"]}
    entries = {DAY: [
        {"home": "Pafos", "away": "Dinamo Tirana", "outcome": "home"},
        {"home": "Pafos FC", "away": "Dinamo Tirana", "outcome": "away"}]}
    assert at.enhancement_leg_result(leg, DAY, _scores_for([("Pafos", "Dinamo Tirana", 3, 0)]),
                                     entries) == "conflict"


def test_run_two_settles_the_frozen_card_through_the_shared_lifecycle(tmp_path, _tmp_lane):
    """§2/§5(2): the crash is gone by construction — run 1 freezes, run 2 settles."""
    _board(_tmp_lane, _distinct(4))
    state = _freeze_now(_tmp_lane)
    bank0 = state["bank"]
    staked = state["open_slips"][0]["staked_pct"]
    assert staked == pytest.approx(25.0)
    scores = _scores_for([
        ("Alpha FC", "Beta FC", 3, 0),       # over 2.5 in acca #1
        ("Eta FC", "Theta FC", 4, 1),        # over 2.5 in acca #1
        ("Gamma FC", "Delta FC", 1, 0)])     # acca #2 is decided by this loss
    # (Epsilon FC has no score yet — a settled LOSING leg decides the acca
    # anyway, bookmaker rules, which is the shared early-loss path.)
    lines = at.settle_open_slips(state, {}, archives=[], entries_by_date={},
                                 lane=at.ENHANCEMENT_LANE, scores=scores)
    # bank moved by ret - staked, per acca; history grew; nothing left open
    assert state["open_slips"] == []
    h = state["history"][-1]
    assert h["date"] == DAY
    assert h["staked_pct"] == pytest.approx(25.0)
    assert [a["won"] for a in h["accas"]] == [True, False]
    win_ret = round(12.5 * h["accas"][0]["odds"], 4)
    assert h["returned_pct"] == pytest.approx(win_ret)
    assert state["bank"] == pytest.approx(bank0 + win_ret - staked)
    assert any("settled 2026-10-12 acca" in l for l in lines)
    assert any("legs=['win', 'win']" in l for l in lines)
    assert any("(decided by settled loss leg)" in l for l in lines)
    # idempotent: a second settle has nothing to do and moves nothing
    bank_after = state["bank"]
    assert at.settle_open_slips(state, {}, archives=[], entries_by_date={},
                                lane=at.ENHANCEMENT_LANE, scores=scores) == []
    assert state["bank"] == bank_after


def test_the_settle_writes_the_lanes_own_state_and_the_main_file_stays_absent(tmp_path, _tmp_lane):
    """The settle is part of the lane's lifecycle, not a route into main's."""
    _board(_tmp_lane, _distinct(2))
    state = _freeze_now(_tmp_lane)
    main_file = _tmp_lane / "auto_tickets_state.json"
    assert not main_file.exists()
    frozen = state["open_slips"][0]
    staked = frozen["staked_pct"]                              # one acca, 12.5%
    acca = frozen["accas"][0]
    scores = _scores_for([("Alpha FC", "Beta FC", 3, 0), ("Gamma FC", "Delta FC", 2, 1)])
    lines = at.settle_open_slips(state, {}, archives=[], entries_by_date={},
                                 lane=at.ENHANCEMENT_LANE, scores=scores)
    saved = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())
    assert saved["open_slips"] == []
    # the shared arithmetic: bank moves by returned - staked, per acca
    assert saved["bank"] == pytest.approx(100.0 + acca["stake_pct"] * acca["odds"] - staked)
    assert saved["history"][-1]["returned_pct"] == pytest.approx(
        acca["stake_pct"] * acca["odds"])
    assert any("settled 2026-10-12 acca" in l for l in lines)
    # the lane's bank move must never land in the main lane's file
    assert not main_file.exists()


def test_a_missing_score_holds_the_leg_and_the_slip_date_timer_voids_it(tmp_path, _tmp_lane):
    """No score is 'not known yet' — the shared void horizon closes it out."""
    import datetime as _dt
    _board(_tmp_lane, _distinct(2))
    state = _freeze_now(_tmp_lane)
    assert at.settle_open_slips(state, {}, archives=[], entries_by_date={},
                                lane=at.ENHANCEMENT_LANE, scores={}) == []
    assert len(state["open_slips"]) == 1 and state["history"] == []
    state["open_slips"][0]["date"] = (
        _dt.datetime.now(at.TZ) - _dt.timedelta(days=6)).strftime("%Y-%m-%d")
    lines = at.settle_open_slips(state, {}, archives=[], entries_by_date={},
                                 lane=at.ENHANCEMENT_LANE, scores={})
    assert state["open_slips"] == []
    assert state["bank"] == pytest.approx(100.0)          # stake returned
    assert state["history"][-1]["returned_pct"] == pytest.approx(
        state["history"][-1]["staked_pct"])
    assert any("legs=['void', 'void']" in l for l in lines)


def test_the_main_lanes_legs_never_carry_a_market():
    """The settle's market path is unreachable for a main-lane card."""
    pool = [{"match": "A vs B", "pick": "home", "prob": 0.5, "odds": 2.0},
            {"match": "C vs D", "pick": "away", "prob": 0.5, "odds": 2.0}]
    plan = at.plan_day(pool, 100.0)
    assert set(plan[0]["legs"][0]) == {"match", "pick", "prob", "odds", "result"}


def test_the_flag_off_means_the_lane_does_nothing(tmp_path, _tmp_lane, monkeypatch):
    monkeypatch.delenv(at.ENH_BOARD_FLAG, raising=False)
    assert at.enhancement_board_enabled() is False
    _board(_tmp_lane, [_pick(price=1.72)])
    rc = at.cmd_enhancement(_args(), at.fresh_state())
    assert rc == 0
    assert not list(_tmp_lane.glob("enhancement_tickets_*.txt"))
    assert not at.ENHANCEMENT_LANE.state_file.exists()


def test_the_main_lane_never_captures_a_state_path_at_import(tmp_path, monkeypatch):
    """REGRESSION: a `Lane` holding `STATE_FILE` as a value freezes whichever
    path existed at import. `STATE_FILE` is the seam every test and tool in the
    repo redirects to keep writes out of the committed ledger; capturing it made
    main-lane tests write into `localdata/auto_tickets_state.json` and truncate
    811 lines of real state (measured 2026-10-12). Main-lane resolution must go
    through `state_path()` at call time.
    """
    monkeypatch.setattr(at, "STATE_FILE", tmp_path / "tickets_state.json")
    assert at.state_path(None) == at.STATE_FILE
    assert at.state_path(at.MAIN_LANE) == at.STATE_FILE
    assert at.state_path(at.ENHANCEMENT_LANE) == at.ENHANCEMENT_LANE.state_file
    at.save_state({"bank": 1.0}, lane=None)
    assert (tmp_path / "tickets_state.json").exists()
    assert at.load_state(lane=None)["bank"] == 1.0
    # the enhancement lane writes only its own file, never the main one
    at.save_state({"bank": 2.0}, lane=at.ENHANCEMENT_LANE)
    assert at.load_state(lane=None)["bank"] == 1.0
    assert at.load_state(lane=at.ENHANCEMENT_LANE)["bank"] == 2.0


def test_the_main_lane_state_schema_is_the_lane_schema():
    """Same schema, so --status and settlement read identically in both lanes."""
    st = at.fresh_state()
    assert set(st) == {"base_pct", "bank", "cycle_base", "open_slips",
                       "history", "events"}
    assert st["base_pct"] == at.BASE_PCT == 100.0


def test_take_profit_uses_the_shared_rule_and_its_own_marker(tmp_path, _tmp_lane):
    st = at.fresh_state()
    st["bank"] = 190.0
    assert at.take_profit_target(st) == pytest.approx(200.0)   # cycle_base x2
    events = at._apply_settlement(st, 25.0, 15.0, DAY, at.ENHANCEMENT_LANE)
    assert st["bank"] == pytest.approx(200.0)
    assert events and "TAKE-PROFIT" in events[0]
    assert at.take_profit_target(st) == pytest.approx(400.0)   # new cycle baseline
    assert (_tmp_lane / f"enhancement_tickets_takeprofit_{DAY}.json").exists()
    assert not (_tmp_lane / f"auto_tickets_takeprofit_{DAY}.json").exists()


def test_record_outcome_carries_slice_provenance_without_moving_the_dedup_key(tmp_path):
    res = reg.record_outcome(tmp_path, date_=DAY, match="A vs B", market="match_over_25",
                             price=1.72, hit=True, source="oddspapi",
                             bucket="CERTIFIED_CLEAN", rule="r1", stated=0.46)
    assert res == {"status": "PAPER", "recorded": True}
    entry = reg._read(reg.registry_path(tmp_path))["markets"]["match_over_25@v1"]
    rec = entry["records"][0]
    assert (rec["bucket"], rec["rule"], rec["stated"]) == ("CERTIFIED_CLEAN", "r1", 0.46)
    # idempotent: the dedup key is unchanged, so a repeat is still a no-op
    again = reg.record_outcome(tmp_path, date_=DAY, match="A vs B", market="match_over_25",
                               price=1.72, hit=True, source="other",
                               bucket="SKIPPED_VETO", rule="r2", stated=0.99)
    assert again["recorded"] is False
    entry = reg._read(reg.registry_path(tmp_path))["markets"]["match_over_25@v1"]
    assert len(entry["records"]) == 1 and entry["records"][0]["bucket"] == "CERTIFIED_CLEAN"


def test_record_outcome_without_provenance_reports_unattributed(tmp_path):
    reg.record_outcome(tmp_path, date_=DAY, match="A vs B", market="match_over_25",
                       price=1.72, hit=False, source="oddspapi")
    rec = reg._read(reg.registry_path(tmp_path))["markets"]["match_over_25@v1"]["records"][0]
    assert rec["bucket"] == "" and rec["rule"] == "" and rec["stated"] is None
    assert reg.slice_for_market(tmp_path, "match_over_25", "bucket") == {
        reg.UNATTRIBUTED: {"n": 1, "hits": 0, "profit": -1.0, "rate": 0.0}}


# --------------------------------------------------------------------------
# acceptance: the floor boundary, the board line, and symmetric pricing
# --------------------------------------------------------------------------

def test_the_floor_boundary_is_inclusive_across_every_floored_market():
    """At the floor is a bet; a hair under it is not — for every market."""
    for market, floor in reg.ENHANCEMENT_PRICE_FLOORS.items():
        assert reg.floor_for(market) == floor
        assert reg.clears_floor(market, floor) is True, market
        assert reg.clears_floor(market, floor - 0.01) is False, market
        assert reg.clears_floor(market, reg.floor_for(market) + 5.0) is True, market
    # The floors are the stated literals, in one place, not scattered calls.
    assert reg.ENHANCEMENT_PRICE_FLOORS == {
        "match_over_25": 1.60, "match_over_15": 1.45,
        "match_over_35": 3.30, "btts_yes": 1.85}


def test_the_board_shows_a_bet_above_the_floor_and_no_bet_below_it():
    """One gate, two presentations: 🔬 for a bet, 🚫 for the refusal."""
    import picks_today as pt

    fired = pt.enhancement_board_line(_pick(price=1.60))      # exactly at floor
    assert fired.startswith("     🔬 ") and "@ 1.60" in fired

    refused = pt.enhancement_board_line(_pick(price=1.59))
    assert refused.startswith("     🚫 ")
    assert "no bet: below match_over_25 floor 1.60" in refused
    # The marker is not advice: nothing about the refused line invites a bet.
    assert "🔬" not in refused

    # A floorless market is not "below" a floor it does not have.
    floorless = pt.enhancement_board_line(_pick(market="away_under_35", price=1.90))
    assert "no bet: no floor set for this market" in floorless

    # Nothing to say when there is no price, or when the price is junk.
    assert pt.enhancement_board_line(_pick(price=None)) is None
    for junk in (1.0, float("nan"), "1.72", True):
        assert pt.enhancement_board_line(_pick(price=junk)) is None
    assert pt.enhancement_board_line({"home": "A", "away": "B"}) is None


def test_the_board_and_the_slip_refuse_with_the_same_floor():
    """The board's gate IS the slip's gate — no second opinion anywhere."""
    import picks_today as pt

    for price in (1.59, 1.60, 1.72, 3.29, 3.30):
        pick = _pick(price=price)
        leg = at.enhancement_legs([pick])[0]
        board_bet = pt.enhancement_board_line(pick).startswith("     🔬 ")
        assert board_bet == (leg["verdict"] == "fire") == reg.clears_floor(
            pick["recommended_enhancement"], price), price
    assert at.enhancement_legs([_pick(price=1.59)])[0]["floor"] == 1.60
    # ...and the slip says "no floor set" for the floorless case rather than
    # claiming the market is below a threshold that does not exist.
    assert at.enhancement_legs([_pick(market="away_under_35", price=1.90)])[0]["floor"] is None


def test_an_under_is_priced_as_readily_as_an_over(tmp_path):
    """MARKET_PRICE_MAP is symmetric: the same capture prices both sides.

    A map that quietly drops one side would leave "under" enhancements
    permanently unpriced — indistinguishable, downstream, from a market no feed
    carries. This pins that a single `ou_2.5/under` row prices `match_under_25`
    exactly as an `ou_2.5/over` row prices `match_over_25`, from one file, with
    attribution, and with no side preference in the merge.
    """
    import gzip
    from edgefactory.enh_pricing import attach_enhancement_price, load_prices_index

    localdata = tmp_path / "localdata"
    localdata.mkdir(parents=True, exist_ok=True)
    cols = ["source", "date", "home", "away", "market", "selection", "odds",
            "bookmaker", "captured_at"]
    rows = [
        ["theoddsapi", DAY, "Alpha FC", "Beta FC", "ou_2.5", "over", "1.72", "Book A", "2026-10-12T01:00:00Z"],
        ["theoddsapi", DAY, "Alpha FC", "Beta FC", "ou_2.5", "under", "2.30", "Book A", "2026-10-12T01:00:00Z"],
    ]
    with gzip.open(localdata / "theoddsapi_odds_2026-10.csv.gz", "wt", newline="") as fh:
        fh.write(",".join(cols) + "\n")
        for r in rows:
            fh.write(",".join(r) + "\n")

    index = load_prices_index(tmp_path, DAY)
    over = attach_enhancement_price(
        {"home": "Alpha FC", "away": "Beta FC", "recommended_enhancement": "match_over_25",
         "pick": "home"}, index)
    under = attach_enhancement_price(
        {"home": "Alpha FC", "away": "Beta FC", "recommended_enhancement": "match_under_25",
         "pick": "home"}, index)
    assert (over["enhancement_price"], over["enhancement_price_source"]) == (1.72, "theoddsapi")
    assert (under["enhancement_price"], under["enhancement_price_source"]) == (2.30, "theoddsapi")
    assert over["enhancement_priced"] is True and under["enhancement_priced"] is True
    # The under is a real product with a real price; it is gated by the floor
    # table (no floor for match_under_25 today), never by the pricing path.
    assert reg.floor_for("match_under_25") is None
    assert reg.clears_floor("match_under_25", 2.30) is False


def test_the_track_record_render_quotes_floor_and_breakeven_per_market(tmp_path):
    """The operator's view of the numbers the floors come from."""
    import audit_recent_picks as au

    root = tmp_path
    (root / "localdata" / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {
            "match_over_25@v1": {"status": "PAPER", "n": 100, "hits": 66,
                                 "profit": 2.297, "records": []},
            "btts_yes@v1": {"status": "PAPER", "n": 7, "hits": 4,
                            "profit": 1.99, "records": []},
            "match_over_45@v1": {"status": "PAPER", "n": 1, "hits": 1,
                                 "profit": 5.6, "records": []},
        }}), encoding="utf-8")
    out = au.render_track_record(root)
    assert "ENHANCEMENT MARKET TRACK RECORD" in out
    assert "match_over_25" in out and "1.515" in out and "1.60" in out   # breakeven, floor
    assert "66.0%" in out and "+2.297u" in out
    assert "⚠ small-n" in out                       # n=7 and n=1 flagged
    assert "none" in out                            # match_over_45 has no floor
    assert "PAPER" in out


def test_the_track_record_render_flags_a_floor_under_its_breakeven(tmp_path):
    """A floor that cannot pay for itself must be visible, not buried."""
    import audit_recent_picks as au

    root = tmp_path
    (root / "localdata" / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {
            "match_over_25@v1": {"status": "PAPER", "n": 100, "hits": 60,
                                 "profit": -1.0, "records": []},
        }}), encoding="utf-8")
    out = au.render_track_record(root)
    assert "1.667" in out                            # breakeven = 1/0.60
    assert "⚠ floor below breakeven" in out          # 1.60 < 1.667


def test_the_track_record_render_is_honest_with_no_history(tmp_path):
    import audit_recent_picks as au

    assert "no settled enhancement history yet" in au.render_track_record(tmp_path)


def test_enhancements_with_the_flag_off_is_a_no_op_not_the_main_lane(monkeypatch, capsys):
    """REGRESSION: `--enhancements` without the flag must do nothing.

    It used to fall through to the main lane, whose default path printed the
    AUTO TICKETS status block — so a daily step labelled "enhancement tickets"
    would report the main lane's performance and imply the enhancement lane was
    live while it was off. Enablement passes this flag (see
    docs/operator/enhancement-lane.yml.proposed), so the flag-off path has to be
    inert and say why.
    """
    monkeypatch.delenv(at.ENH_BOARD_FLAG, raising=False)
    monkeypatch.setattr(at.sys, "argv", ["auto_tickets.py", "--enhancements"])
    monkeypatch.setattr(at, "load_state", _boom)   # main-lane state must not be read
    monkeypatch.setattr(at, "cmd_today", _boom)
    assert at.main() == 0
    out = capsys.readouterr().out
    assert f"{at.ENH_BOARD_FLAG}=1" in out and "nothing done" in out
    assert "AUTO TICKETS" not in out


def _boom(*a, **k):   # pragma: no cover - only reached on regression
    raise AssertionError("the disabled enhancement lane must not touch the main lane")


# --------------------------------------------------------------------------
# R2: the derived per-slice floors reach the board, the slip and the state
# --------------------------------------------------------------------------

def _tightened_registry(localdata: Path) -> dict:
    """A registry whose market slice clears the gate and tightens the floor.

    40 priced records, 18 hits: Wilson LB95 ~0.30 -> 1/LB + 0.10 ~ 3.4, well
    above the operator's 1.60 for match_over_25. The same table is what the
    derivation prints, so the tests assert the numbers the code derives.
    """
    recs = []
    for i in range(40):
        recs.append({"date": f"2026-09-{i % 28 + 1:02d}", "match": f"T{i} vs U{i}",
                     "price": 1.9, "hit": (i < 18), "source": "oddspapi",
                     "multi_source": False, "bucket": "", "rule": "", "stated": None,
                     "league": "Testland,Liga", "home": f"T{i}", "away": f"U{i}",
                     "home_key": f"t{i}", "away_key": f"u{i}"})
    payload = {"version": 2, "markets": {"match_over_25@v1": {
        "status": "PAPER", "n": 40, "hits": 18, "profit": -1.0, "inv_price_sum": 20.0,
        "multi_n": 0, "processed": [], "records": recs}}}
    (localdata / "enhancement_registry.json").write_text(json.dumps(payload))
    return payload


def test_the_derived_floor_tightens_the_market_and_the_slip_and_the_board_agree(tmp_path, _tmp_lane):
    import picks_today as pt
    _tightened_registry(_tmp_lane)
    floors = reg.derive_floors_for_day(_tmp_lane.parent, DAY)
    market_row = [r for r in floors["rows"] if r["level"] == "market"][0]
    assert market_row["basis"] == "market"
    derived = market_row["floor"]
    assert derived > reg.floor_for("match_over_25")

    # A price that clears the OPERATOR's floor and not the derived one is not a
    # bet on either surface — and both surfaces say which floor refused it.
    price = round(reg.floor_for("match_over_25") + 0.01, 2)
    pick = _pick(price=price)
    leg = at.enhancement_legs([pick], floors=floors)[0]
    assert leg["verdict"] == "below_floor"
    assert leg["floor"] == derived and leg["floor_basis"] == "market"
    board = pt.enhancement_board_line(pick, floors=floors)
    assert board.startswith("     🚫 ")
    assert f"below match_over_25 floor {derived:.2f} (market)" in board
    # ...and the same price against the operator's table (no derived rows) fires
    assert at.enhancement_legs([pick], floors={})[0]["verdict"] == "fire"
    assert pt.enhancement_board_line(pick, floors={}).startswith("     🔬 ")
    # A price above the derived floor fires on both, quoting the basis.
    above = _pick(price=round(derived + 0.05, 2))
    assert at.enhancement_legs([above], floors=floors)[0]["verdict"] == "fire"
    assert f"floor {derived:.2f} (market)" in pt.enhancement_board_line(above, floors=floors)


def test_the_lane_artifact_and_state_carry_the_days_derivation(_tmp_lane):
    _tightened_registry(_tmp_lane)
    _board(_tmp_lane, _distinct(4, price=4.10))
    st = at.fresh_state()
    rc = at.cmd_enhancement(_args(), st)
    assert rc == 0
    artifact = (_tmp_lane / f"{at.ENHANCEMENT_LANE.slip_prefix}_{DAY}.txt").read_text()
    assert "FLOORS (derived for" in artifact
    assert "margin 0.100" in artifact and "Wilson LB" in artifact
    assert f"match_over_25" in artifact and "basis" in artifact
    # the derived floor, not the operator's, is the number on the leg lines
    floors = reg.derive_floors_for_day(_tmp_lane.parent, DAY)
    derived = [r for r in floors["rows"] if r["level"] == "market"][0]["floor"]
    assert f"floor {derived:.2f} (market)" in artifact
    # the state the lane persists carries the same table
    saved = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())
    table = saved.get("enh_floor_table")
    assert table and table["as_of"] == DAY
    assert table["margin"] == reg.ENHANCEMENT_FLOOR_MARGIN
    assert table["min_n"] == reg.MIN_PRICED_N
    assert table["floors"]["match_over_25"]["basis"] == "market"
    assert table["floors"]["match_over_25"]["floor"] == derived
    assert table["coverage"]["with_league"] == 40


def test_a_team_slice_is_never_consulted_for_a_leg(tmp_path, _tmp_lane):
    """The report-only rule, through the shipped entry points."""
    import picks_today as pt
    payload = _tightened_registry(_tmp_lane)
    recs = payload["markets"]["match_over_25@v1"]["records"]
    for rec in recs[:30]:                       # Team T0 rides 30 of the 40 records
        rec["home"], rec["home_key"] = "T0", "t0"
    ( _tmp_lane / "enhancement_registry.json").write_text(json.dumps(payload))
    floors = reg.derive_floors_for_day(_tmp_lane.parent, DAY)
    team_rows = [r for r in floors["rows"] if r["level"] == "team" and r["team"] == "t0"]
    assert team_rows, "the team slice must be reported"
    assert team_rows[0]["basis"] == "team" and "not applied" in team_rows[0]["reason"]
    applied, basis = reg.floor_for_slice(floors, "match_over_25", "Testland,Liga")
    assert basis != "team"                       # never the team number
    assert applied == [r for r in floors["rows"]
                       if r["level"] == "league"][0]["floor"]
    pick = _pick(price=round(applied + 0.02, 2))
    assert at.enhancement_legs([pick], floors=floors)[0]["verdict"] == "fire"
    assert pt.enhancement_board_line(pick, floors=floors).startswith("     🔬 ")
