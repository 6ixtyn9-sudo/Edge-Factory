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

from enhancement_fixtures import with_evidence

DAY = "2026-10-12"


def _pick(home="Pyunik Yerevan", away="BKMA", market="match_over_25", *,
          price=1.72, bucket="CERTIFIED_CLEAN", rule="r1", prob=0.46,
          label="Match Over 2.5 Goals", book="Stake.com"):
    # A real card row always carries a kickoff; the live guard withdraws legs
    # without one. Default to a kickoff still ahead of the pinned 08:00 SAST run.
    return with_evidence({"home": home, "away": away, "match": f"{home} vs {away}", "date": DAY,
            "bucket": bucket, "rule": rule, "recommended_enhancement": market,
            "enhancement_label": label, "enhancement_probability": prob,
            "enhancement_price": price, "enhancement_price_book": book,
            "enhancement_price_source": "oddspapi",
            "kickoff_utc": f"{DAY}T16:00:00+00:00"})


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
        localdata / "enhancement_tickets_state.json", "autobets_enh_tickets",
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
    """No EV veto and no price floor: a leg with a big sample edge fires at any
    price above the minimum; only a price under MIN_LEG_ODDS is refused."""
    above = _pick(price=1.59, prob=0.95)
    below = _pick(price=1.25, prob=0.95)
    legs = {l["price"]: l for l in at.enhancement_legs([above, below])}
    assert legs[1.59]["verdict"] == "fire"
    assert legs[1.25]["verdict"] == "below_min_odds"
    # The information fields remain on the row; nothing consults them here.
    assert below.get("enhancement_edge_sample") is None  # set by enh_pricing, not here


def test_unpriced_and_unpriceable_legs_do_not_fire():
    unpriced = _pick(market="match_over_35", price=None)
    # A market no feed maps is unpriceable; a mapped team total is merely unpriced.
    unpriceable = _pick(market="goal_range_2_3", price=None)
    team_total = _pick(market="home_under_35", price=None)
    legs = {l["market"]: l for l in at.enhancement_legs([unpriced, unpriceable, team_total])}
    assert legs["match_over_35"]["verdict"] == "unpriced"
    assert legs["goal_range_2_3"]["verdict"] == "unpriceable"
    assert legs["home_under_35"]["verdict"] == "unpriced"
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


def _distinct(n, market="match_over_25", price=1.80, **kw):
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
                       rank=at.ENHANCEMENT_RANK, fixture_report=report)
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
    assert "(realized 46%, n=200)" in txt
    assert "[registry" not in txt and "floor 1.60" not in txt
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


def test_a_same_fixture_duplicate_is_dropped_and_reported(tmp_path, _tmp_lane):
    """B-1's eligibility: priced, clearing its floor, and not a fixture dupe."""
    _board(_tmp_lane, [
        _pick(market="match_over_25", price=1.80, prob=0.40),
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
    assert "Pyunik Yerevan vs BKMA" not in txt   # the card reports no diagnostics
    assert "NO BET — only 1 eligible leg(s), need 2 for an acca" in txt


def test_a_vetoed_parent_is_staked_and_not_called_paper(tmp_path, _tmp_lane):
    """SKIPPED_VETO is ticket-eligible under BUCKETS, so its legs are real stakes.

    The old tag said \"paper\" while the plan staked the same legs. The tag now
    only names the parent bucket, and the stake is what the plan computed.
    """
    _board(_tmp_lane, _distinct(2, bucket="SKIPPED_VETO"))
    legs, plan = _legs_and_plan(_tmp_lane)
    assert plan and all(a["stake_pct"] > 0 for a in plan)
    assert all(l.get("shadow") for a in plan for l in a["legs"])
    txt = at.render_enhancement_tickets(at.fresh_state(), DAY, legs, plan, _now(),
                                        should_freeze=False, freeze_record=None,
                                        bank_eff=100.0)
    acca_line = next(l for l in txt.splitlines() if l.startswith("[ACCA #1]"))
    assert acca_line.endswith(at.ENH_SHADOW_TAG)
    assert "paper" not in txt.lower()


def test_the_artifact_matches_autobets_conventions(tmp_path, _tmp_lane):
    _registry(_tmp_lane)
    _board(_tmp_lane, _distinct(2) + [
        _pick(home="Nu FC", away="Xi FC", price=1.20)])       # below the minimum
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
    # the card carries no diagnostics tables and no per-leg refusals
    assert "ENHANCEMENT SLICE" not in txt and "FLOORS" not in txt
    assert "[NO BET]" not in txt and "1.20" not in txt
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
    art = _tmp_lane / f"autobets_enh_tickets_{DAY}.txt"
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
        # ...and --force may not rewrite it either: it writes a re-cut report
        # beside it instead (see the recut tests below).
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
    assert (_tmp_lane / f"autobets_enh_tickets_{DAY}.txt").exists()


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


def test_a_leg_is_graded_from_the_staked_days_score_not_an_earlier_same_name_fixture():
    """A same-named fixture on an earlier day must not grade the staked leg."""
    leg = {"market": "home_under_15", "pick": "home", "match": "Mito Hollyhock vs FC Tokyo",
           "fixture_key": [DAY, "Mito Hollyhock", "FC Tokyo"]}
    earlier = _scores_for([("Mito Hollyhock", "FC Tokyo", 3, 0)], day="2026-10-11")
    on_day = _scores_for([("Mito Hollyhock", "FC Tokyo", 1, 0)])
    scores = {**earlier, **on_day}
    # home scored 1 on the staked day -> Under 1.5 wins; the 3-0 on an
    # earlier date must not be picked up first.
    assert at.enhancement_leg_result(leg, DAY, scores) == "win"
    # with only the earlier-date score present, it is still found (within window)
    assert at.enhancement_leg_result(leg, DAY, earlier) == "loss"


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
    # The settle reads the void clock through ``at.datetime``, which _tmp_lane
    # pins to DAY 08:00. The slip date must come from that same clock, not the
    # real one, or the horizon depends on the day the test happens to run.
    state["open_slips"][0]["date"] = (
        at.datetime.now(at.TZ) - _dt.timedelta(days=6)).strftime("%Y-%m-%d")
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
    assert (_tmp_lane / f"autobets_enh_tickets_takeprofit_{DAY}.json").exists()
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
            "match_over_35": 3.30, "btts_yes": 1.85,
            "match_under_15": 4.45, "match_under_25": 2.38,
            "match_under_35": 1.64}


def test_the_board_shows_a_bet_at_the_minimum_and_no_bet_below_it():
    """One gate, two presentations: 🔬 for a bet, 🚫 for the refusal."""
    import picks_today as pt
    from auto_tickets import MIN_LEG_ODDS

    fired = pt.enhancement_board_line(_pick(price=MIN_LEG_ODDS))   # exactly at the minimum
    assert fired.startswith("     🔬 ") and f"@ {MIN_LEG_ODDS:.2f}" in fired

    refused = pt.enhancement_board_line(_pick(price=round(MIN_LEG_ODDS - 0.01, 2)))
    assert refused.startswith("     🚫 ")
    assert f"no bet: below minimum {MIN_LEG_ODDS:.2f}" in refused
    # The marker is not advice: nothing about the refused line invites a bet.
    assert "🔬" not in refused

    # A floorless market that is not a team under fires: no floor gate any more.
    assert pt.enhancement_board_line(_pick(market="match_over_45", price=3.75)).startswith("     🔬 ")
    # A realized-contract-backed team under competes without a price floor.
    assert pt.enhancement_board_line(_pick(market="away_under_35", price=1.90)).startswith("     🔬 ")
    # But a model-only row is refused by BOTH presentations, regardless of price.
    model = _pick(market="away_under_35", price=1.90)
    model.pop("event_notes")
    assert "no bet: no valid realized contract-cohort evidence" in pt.enhancement_board_line(model)
    assert at.enhancement_legs([model])[0]["verdict"] == "no_cohort_evidence"

    # Nothing to say when there is no price, or when the price is junk.
    assert pt.enhancement_board_line(_pick(price=None)) is None
    for junk in (1.0, float("nan"), "1.72", True):
        assert pt.enhancement_board_line(_pick(price=junk)) is None
    assert pt.enhancement_board_line({"home": "A", "away": "B"}) is None


def test_there_is_no_price_ceiling_any_price_above_the_minimum_fires(tmp_path, _tmp_lane):
    """Operator 2026-10-14: accept whatever odds. The old 1.85 band is gone."""
    for price in (1.85, 1.86, 3.50):
        assert at.enhancement_legs([_pick(price=price)])[0]["verdict"] == "fire", price


def test_the_board_and_the_slip_refuse_with_the_same_minimum():
    """The board's gate IS the slip's gate: the MIN_LEG_ODDS minimum, nothing else."""
    import picks_today as pt
    for price in (1.25, 1.29, 1.30, 1.59, 1.86, 3.50):
        pick = _pick(price=price)
        leg = at.enhancement_legs([pick])[0]
        board_bet = pt.enhancement_board_line(pick).startswith("     🔬 ")
        assert board_bet == (leg["verdict"] == "fire") == (price >= at.MIN_LEG_ODDS), price


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
    # table (base-rate floor 2.38 for match_under_25), never by the pricing path.
    assert reg.floor_for("match_under_25") == 2.38
    assert reg.clears_floor("match_under_25", 2.30) is False
    assert reg.clears_floor("match_under_25", 2.40) is True


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


def test_a_derived_floor_no_longer_gates_a_leg(tmp_path, _tmp_lane, monkeypatch):
    """Operator 2026-10-14: no floor gate. A price under the derived floor but at or
    above the minimum fires on the slip and on the board."""
    import picks_today as pt
    monkeypatch.setattr(reg, "ENHANCEMENT_PRICE_CEILINGS", {})
    _tightened_registry(_tmp_lane)
    floors = reg.derive_floors_for_day(_tmp_lane.parent, DAY)
    pick = _pick(price=1.50)
    assert at.enhancement_legs([pick], floors=floors)[0]["verdict"] == "fire"
    assert pt.enhancement_board_line(pick, floors=floors).startswith("     🔬 ")


def test_the_lane_state_carries_the_days_derivation(_tmp_lane, monkeypatch):
    monkeypatch.setattr(reg, "ENHANCEMENT_PRICE_CEILINGS", {})   # floor-only test
    _tightened_registry(_tmp_lane)
    _board(_tmp_lane, _distinct(4, price=4.10))
    st = at.fresh_state()
    rc = at.cmd_enhancement(_args(), st)
    assert rc == 0
    artifact = (_tmp_lane / f"{at.ENHANCEMENT_LANE.slip_prefix}_{DAY}.txt").read_text()
    # the card carries no derivation table; the derivation lives in the state
    assert "FLOORS (derived for" not in artifact
    # the state the lane persists carries the same table
    saved = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())
    table = saved.get("enh_floor_table")
    assert table and table["as_of"] == DAY
    assert table["margin"] == reg.ENHANCEMENT_FLOOR_MARGIN
    assert table["min_n"] == reg.MIN_PRICED_N
    assert table["floors"]["match_over_25"]["basis"] == "market"
    floors = reg.derive_floors_for_day(_tmp_lane.parent, DAY)
    derived = [r for r in floors["rows"] if r["level"] == "market"][0]["floor"]
    assert table["floors"]["match_over_25"]["floor"] == derived
    assert table["coverage"]["with_league"] == 40


def test_a_team_slice_is_never_consulted_for_a_leg(tmp_path, _tmp_lane, monkeypatch):
    """The report-only rule, through the shipped entry points."""
    import picks_today as pt
    monkeypatch.setattr(reg, "ENHANCEMENT_PRICE_CEILINGS", {})   # floor-only test
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


def test_enhancement_slips_are_named_and_tracked_beside_autobets():
    """The enhancement slip is autobets_enh_tickets_<day>.txt and is NOT ignored
    by git, so it is committed to main like the main lane's auto_tickets slip.
    The state file stays ignored (runtime state)."""
    import subprocess
    from pathlib import Path
    root = Path(__file__).resolve().parent.parent
    # The autouse fixture patches ENHANCEMENT_LANE, so read the production
    # declaration from the module source instead of the patched constant.
    src = Path(at.__file__).read_text(encoding="utf-8")
    assert 'Lane(ENHANCEMENT_STATE_FILE, "autobets_enh_tickets"' in src
    slip = f"localdata/{at.ENHANCEMENT_LANE.slip_prefix}_{DAY}.txt"
    state = "localdata/enhancement_tickets_state.json"
    if not (root / ".git").exists():
        pytest.skip("not a git checkout")
    ign = subprocess.run(["git", "check-ignore", "-q", slip], cwd=root)
    assert ign.returncode == 1, "enhancement slip must not be gitignored"
    ign_state = subprocess.run(["git", "check-ignore", "-q", state], cwd=root)
    assert ign_state.returncode == 0, "enhancement state file stays ignored"


# ---- ranking by hit rate (approved 2026-10-13) ------------------------------
# Every floor is 1 / Wilson-LB95(hit rate) + ENHANCEMENT_FLOOR_MARGIN, so the
# enhancement lane ranks by the hit rate the floor encodes, not by the model's
# stated probability. Stated probability only breaks ties.

def _ranked_leg(match, market_floor, *, prob, odds=2.0):
    home, away = match.split(" vs ")
    return {"match": match, "pick": "over", "prob": prob, "odds": odds,
            "row": {"home": home, "away": away, "date": "2026-10-13"},
            "floor": market_floor, "market": "x"}


def test_the_implied_hit_rate_is_recovered_from_the_floor():
    from edgefactory.enh_registry import ENHANCEMENT_FLOOR_MARGIN
    assert ENHANCEMENT_FLOOR_MARGIN == pytest.approx(0.10)
    # match_over_25: floor 1.60 <-> 1 / 1.50 = 66.7% hit rate
    assert at._implied_hit_chance({"floor": 1.60}) == pytest.approx(1 / 1.50)
    # match_under_15: floor 4.45 <-> 1 / 4.35 = 23.0% hit rate
    assert at._implied_hit_chance({"floor": 4.45}) == pytest.approx(1 / 4.35)
    assert at._implied_hit_chance({"floor": None}) == 0.0
    assert at._implied_hit_chance({}) == 0.0


def test_enhancement_ranks_by_hit_rate_not_stated_probability():
    # The under is stated at 0.90 but its floor says only ~23% hit rate; the
    # over 1.5 is stated at 0.60 but its floor says ~74%. Hit rate wins.
    under = _ranked_leg("Alpha FC vs Beta FC", 4.45, prob=0.90, odds=4.6)
    over = _ranked_leg("Gamma FC vs Delta FC", 1.45, prob=0.60, odds=1.8)
    pool = [under, over]
    assert [l["match"] for l in at.rank_legs(pool, "hitrate")] == [
        "Gamma FC vs Delta FC", "Alpha FC vs Beta FC"]
    # the default (main lane) order is still stated probability
    assert [l["match"] for l in at.rank_legs(pool)] == [
        "Alpha FC vs Beta FC", "Gamma FC vs Delta FC"]


def test_stated_probability_only_breaks_ties_on_equal_hit_rate():
    a = _ranked_leg("Alpha FC vs Beta FC", 1.60, prob=0.55)
    b = _ranked_leg("Gamma FC vs Delta FC", 1.60, prob=0.70)
    assert [l["match"] for l in at.rank_legs([a, b], "hitrate")] == [
        "Gamma FC vs Delta FC", "Alpha FC vs Beta FC"]


def test_a_leg_with_no_floor_ranks_last_under_hitrate():
    nofloor = _ranked_leg("Alpha FC vs Beta FC", None, prob=0.99)
    floored = _ranked_leg("Gamma FC vs Delta FC", 3.30, prob=0.10)
    assert [l["match"] for l in at.rank_legs([nofloor, floored], "hitrate")] == [
        "Gamma FC vs Delta FC", "Alpha FC vs Beta FC"]


def test_the_enhancement_lane_is_the_only_caller_on_hitrate():
    assert at.ENHANCEMENT_RANK == "prob"
    # main lane selection default is untouched
    import inspect
    assert inspect.signature(at.select_accas).parameters["rank"].default == "prob"


def test_a_priced_leg_with_no_floor_prints_no_bet_and_never_crashes(tmp_path, _tmp_lane):
    """A priced team-under has no floor (home/away_under_35), so its leg is
    ``no_floor`` with ``floor=None``. The render used to format that None in
    the ``outlier_price`` text eagerly and raised TypeError, failing the whole
    --enhancements stage (daily run 38509129401). It must print NO BET instead."""
    leg = {
        "match": "Alpha FC vs Beta FC", "home": "Alpha FC", "away": "Beta FC",
        "row": {}, "fixture_key": "k", "market": "away_under_35",
        "label": "AWAY UNDER 3.5", "probability": 0.5, "price": 1.9,
        "price_book": "x", "price_source": "x", "bucket": "SKIPPED_VETO",
        "rule": "", "league": "L", "floor": None, "floor_basis": "inherited",
        "ceiling": None, "verdict": "no_floor", "shadow": True,
    }
    for verdict in ("no_floor", "outlier_price", "below_floor"):
        leg["verdict"] = verdict
        txt = at.render_enhancement_tickets(at.fresh_state(), DAY, [leg], [], _now(),
                                            should_freeze=False, freeze_record=None,
                                            bank_eff=100.0)
        # refusals are not printed on the card; it says no bet and does not crash
        assert "Alpha FC" not in txt, verdict
        assert "NO BET — only 0 eligible leg(s)" in txt, verdict


def test_the_enhancement_lane_builds_three_accas_and_the_main_lane_stays_at_two():
    """Operator, 2026-10-14: the enhancement lane takes 3 accas; the main lane's
    armed MAX_ACCAS stays 2. Both deploy the same 25% day total."""
    assert at.ENH_MAX_ACCAS == 3
    assert at.MAX_ACCAS == 2
    pool = [_ranked_leg(f"Team{i} FC vs Rival{i} FC", None, prob=0.80 - i * 0.02, odds=1.5)
            for i in range(6)]
    enh = at.plan_day(pool, 100.0, stake_frac=0.25, max_accas=at.ENH_MAX_ACCAS,
                      rank="prob")
    main = at.plan_day(pool, 100.0, stake_frac=0.25, rank="prob")
    assert len(enh) == 3
    assert len(main) == 2
    assert sum(a["stake_pct"] for a in enh) == pytest.approx(25.0, abs=0.01)
    assert sum(a["stake_pct"] for a in main) == pytest.approx(25.0, abs=0.01)


# --------------------------------------------------------------------------
# --force on a frozen date: supersede with a recut report, never rewrite
# --------------------------------------------------------------------------

def _force_recut(localdata, board):
    """Freeze DAY with the current board, then re-cut it with `board` under --force."""
    _board(localdata, _distinct(2))                        # the card that gets frozen
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 0)
    try:
        _freeze_now(localdata)
        frozen_text = (localdata / f"autobets_enh_tickets_{DAY}.txt").read_text()
        state_path = localdata / "enhancement_tickets_state.json"
        frozen_state = json.loads(state_path.read_text())
        _board(localdata, board)
        at.cmd_enhancement(_args(force=True), json.loads(state_path.read_text()))
    finally:
        monkey.undo()
    return frozen_text, frozen_state


def test_a_forced_recut_supersedes_the_frozen_card_and_never_edits_it(tmp_path, _tmp_lane):
    frozen_text, frozen_state = _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    art = _tmp_lane / f"autobets_enh_tickets_{DAY}.txt"
    recut = _tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt"
    state = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())

    assert art.read_text() == frozen_text                       # the staked card: untouched
    text = recut.read_text()
    assert text.startswith(f"ENHANCEMENT FORCE RE-CUT — {DAY}")
    assert "The frozen slip was NOT edited" in text
    assert "STAKED on the frozen card, NOT on the re-cut (2)" in text
    assert "ON THE RE-CUT ONLY (2)" in text
    # the frozen acca stays open for settlement, exactly as it was staked
    assert state["open_slips"] == frozen_state["open_slips"]
    assert state["frozen_by_date"] == frozen_state["frozen_by_date"]
    assert "[ACCA #" in text                                   # the re-cut has legs
    assert "superseded_by_date" not in state                   # no state marker


def test_a_forced_recut_with_no_qualifying_leg_is_recorded_as_no_bet(tmp_path, _tmp_lane):
    frozen_text, _ = _force_recut(_tmp_lane, _distinct(2, price=1.10))   # below MIN_LEG_ODDS
    art = _tmp_lane / f"autobets_enh_tickets_{DAY}.txt"
    recut = _tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt"
    state = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())

    assert art.read_text() == frozen_text
    assert "NO BET" in recut.read_text()
    assert "[ACCA #" not in recut.read_text()                  # a no-bet re-cut
    assert state["open_slips"][0]["accas"]                    # frozen acca still open


def test_an_ordinary_run_after_a_recut_shows_the_frozen_card_and_the_notice(tmp_path, _tmp_lane, capsys):
    frozen_text, _ = _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    recut = _tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt"
    recut_before = recut.read_text()
    capsys.readouterr()
    state = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())

    rc = at.cmd_enhancement(_args(), state)
    out = capsys.readouterr().out
    assert rc == 0
    assert frozen_text in out
    assert "SUPERSEDED" in out and "_force_recut.txt" in out
    assert recut.read_text() == recut_before


def _notice_after_run(localdata, capsys) -> str:
    capsys.readouterr()
    state = json.loads((localdata / "enhancement_tickets_state.json").read_text())
    at.cmd_enhancement(_args(), state)
    return capsys.readouterr().out


def test_a_recut_is_stamped_with_the_slate_it_was_built_from(tmp_path, _tmp_lane, capsys):
    _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    recut = (_tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt").read_text()
    assert at._RECUT_SLATE_RE.search(recut) is not None
    out = _notice_after_run(_tmp_lane, capsys)
    assert "CURRENT — built from today's picks_today.json" in out


def test_a_recut_built_from_an_older_slate_is_flagged_stale(tmp_path, _tmp_lane, capsys):
    _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    # the slate moves on after the re-cut was written
    _board(_tmp_lane, _distinct(2, market="btts_yes", price=2.10))
    out = _notice_after_run(_tmp_lane, capsys)
    assert "STALE — built from a different picks_today.json" in out
    assert "CURRENT" not in out


def test_a_recut_with_no_slate_stamp_is_unverified_not_current(tmp_path, _tmp_lane, capsys):
    _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    recut = _tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt"
    recut.write_text("\n".join(
        ln for ln in recut.read_text().splitlines() if not ln.startswith("  slate sha256:")))
    out = _notice_after_run(_tmp_lane, capsys)
    assert "SUPERSEDED" in out and "_force_recut.txt" in out
    assert "UNVERIFIED — this re-cut carries no slate stamp" in out
    assert "CURRENT" not in out


def test_a_frozen_slip_on_disk_locks_the_date_even_without_the_state_file(tmp_path, _tmp_lane):
    _board(_tmp_lane, _distinct(2))
    _freeze_now(_tmp_lane)
    frozen_text = (_tmp_lane / f"autobets_enh_tickets_{DAY}.txt").read_text()
    # a fresh checkout: the gitignored state is gone, the committed slip survives
    (_tmp_lane / "enhancement_tickets_state.json").unlink()
    _board(_tmp_lane, _distinct(2, market="btts_yes", price=2.10))
    at.cmd_enhancement(_args(), at.fresh_state())
    assert (_tmp_lane / f"autobets_enh_tickets_{DAY}.txt").read_text() == frozen_text
    assert not (_tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt").exists()


def test_the_recut_diff_comes_from_the_frozen_slip_when_the_state_is_gone(tmp_path, _tmp_lane):
    """A fresh checkout has no state file; the staked legs still come from the slip."""
    _board(_tmp_lane, _distinct(2))
    _freeze_now(_tmp_lane)
    (_tmp_lane / "enhancement_tickets_state.json").unlink()
    _board(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    at.cmd_enhancement(_args(force=True), at.fresh_state())
    text = (_tmp_lane / f"autobets_enh_tickets_{DAY}_force_recut.txt").read_text()
    assert "frozen_at 08:00 (from the slip)" in text
    assert "STAKED on the frozen card, NOT on the re-cut (2)" in text
    assert "ON THE RE-CUT ONLY (2)" in text
    assert "Alpha FC vs Beta FC  Match Over 1.5 Goals @ 1.80" in text
    assert "frozen legs unknown" not in text


def test_the_superseded_notice_survives_a_fresh_checkout_with_no_state(tmp_path, _tmp_lane, capsys):
    """CI has no state file. The notice must still appear, read from the re-cut file."""
    frozen_text, _ = _force_recut(_tmp_lane, _distinct(2, market="match_over_15", label="Match Over 1.5 Goals"))
    (_tmp_lane / "enhancement_tickets_state.json").unlink()
    capsys.readouterr()
    at.cmd_enhancement(_args(), at.fresh_state())
    out = capsys.readouterr().out
    assert frozen_text in out
    assert "SUPERSEDED — a forced re-cut (RECUT)" in out
    assert "autobets_enh_tickets_2026-10-12_force_recut.txt" in out


def test_a_no_bet_recut_notice_reads_no_bet_from_the_file_alone(tmp_path, _tmp_lane, capsys):
    _force_recut(_tmp_lane, _distinct(2, price=1.10))                   # below MIN_LEG_ODDS
    (_tmp_lane / "enhancement_tickets_state.json").unlink()
    capsys.readouterr()
    at.cmd_enhancement(_args(), at.fresh_state())
    assert "SUPERSEDED — a forced re-cut (NO BET)" in capsys.readouterr().out


def test_enhancement_legs_already_kicked_off_or_finished_are_withdrawn_from_the_card():
    """A draft built after a kickoff must not list that match (2026-10-15 card:
    Marquense 05:00, LA FC 04:30 and Nashville 02:30 were still on it at 07:28)."""
    now = datetime.fromisoformat(f"{DAY}T08:00:00").replace(tzinfo=at.TZ)
    started = _pick(home="Marquense", away="Mixco", price=1.64, market="match_over_25")
    started["kickoff_utc"] = f"{DAY}T05:00:00+00:00"     # 07:00 SAST: already started
    upcoming = _pick(home="Riga FC", away="Kairat Almaty", price=1.30, market="match_over_15")
    upcoming["kickoff_utc"] = f"{DAY}T16:45:00+00:00"    # 18:45 SAST: still ahead
    finished = _pick(home="Alpha FC", away="Beta FC", price=1.50, market="match_over_25")
    finished["kickoff_utc"] = f"{DAY}T16:45:00+00:00"    # ahead, but the score is already in
    legs = at.enhancement_legs([started, upcoming, finished])
    hk, ak = at._result_write_keys("Alpha FC", "Beta FC")[0]
    report = at.apply_enhancement_timing(legs, now, DAY, {(DAY, hk, ak): (1, 0)})
    pool = at.enhancement_pool(legs)
    assert [l["match"] for l in pool] == ["Riga FC vs Kairat Almaty"]
    assert "Marquense vs Mixco" in report[at.KO_SKIP_STARTED]
    assert "Alpha FC vs Beta FC" in report["result already known"]
    by_match = {l["match"]: l for l in legs}
    assert by_match["Marquense vs Mixco"]["verdict"] == "kickoff_guard"
    assert by_match["Alpha FC vs Beta FC"]["verdict"] == "result_known"
    assert by_match["Riga FC vs Kairat Almaty"]["verdict"] == "fire"
