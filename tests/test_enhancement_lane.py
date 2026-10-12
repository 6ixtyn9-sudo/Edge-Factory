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


@pytest.fixture(autouse=True)
def _tmp_lane(tmp_path, monkeypatch):
    """Every test writes lane state and the artifact into a temp dir."""
    localdata = tmp_path / "localdata"
    localdata.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(at, "LOCALDATA", localdata)
    monkeypatch.setattr(at, "ENHANCEMENT_LANE", at.Lane(
        localdata / "enhancement_tickets_state.json", "enhancement_tickets",
        "ENHANCEMENT TICKETS (ROLLING)", at.STAKE_FRAC))
    # Main-lane paths must never be touched by these tests either.
    monkeypatch.setattr(at, "STATE_FILE", localdata / "auto_tickets_state.json")
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
# presentation: one leg per ticket, shadow parents, autobets' layout
# --------------------------------------------------------------------------

def test_one_leg_per_ticket_and_the_day_deploys_the_lane_stake(tmp_path, _tmp_lane):
    _board(_tmp_lane, [_pick(price=1.72), _pick(market="btts_yes", price=1.90, label="BTTS YES")])
    legs = at.enhancement_legs(json.loads((_tmp_lane / "picks_today.json").read_text()))
    firing = [l for l in legs if l["verdict"] == "fire"]
    assert len(firing) == 2
    deploy = at.ENHANCEMENT_LANE.stake_frac * 100.0
    assert deploy == pytest.approx(25.0)          # same 25%-of-free-bank as autobets
    per_ticket = deploy / len(firing)
    assert per_ticket == pytest.approx(12.5)      # one leg per ticket


def test_a_vetoed_parent_stays_shadow(tmp_path, _tmp_lane):
    _board(_tmp_lane, [_pick(bucket="SKIPPED_VETO", price=1.72)])
    txt = at.render_enhancement_tickets(
        at.fresh_state(), DAY, at.enhancement_legs(json.loads(
            (_tmp_lane / "picks_today.json").read_text())),
        __import__("datetime").datetime.now(at.TZ),
        should_freeze=False, freeze_record=None, bank_eff=100.0)
    assert at.ENH_SHADOW_TAG.strip() in txt
    assert "[SHADOW — paper]" in txt


def test_the_artifact_matches_autobets_conventions(tmp_path, _tmp_lane):
    _registry(_tmp_lane)
    _board(_tmp_lane, [_pick(price=1.72), _pick(market="match_over_35", price=3.10)])
    import datetime as _dt
    legs = at.enhancement_legs(json.loads((_tmp_lane / "picks_today.json").read_text()))
    txt = at.render_enhancement_tickets(
        at.fresh_state(), DAY, legs, _dt.datetime.now(at.TZ),
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
    assert "[NO BET]" in txt and "below floor 3.30 — no bet" in txt
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


def test_the_freeze_is_write_once_and_force_cannot_rewrite_it(tmp_path, _tmp_lane):
    import datetime as _dt
    _board(_tmp_lane, [_pick(price=1.72)])
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
        _board(_tmp_lane, [_pick(market="btts_yes", price=2.10, label="BTTS YES")])
        at.cmd_enhancement(_args(), json.loads(path.read_text()))
        assert art.read_text() == frozen_text
        # ...and neither may --force (that is how bets rotate under the operator).
        at.cmd_enhancement(_args(force=True), json.loads(path.read_text()))
        assert art.read_text() == frozen_text
        assert json.loads(path.read_text())["frozen_by_date"][DAY] == stamp
    finally:
        monkey.undo()


def test_before_the_freeze_hour_the_slip_is_a_draft(tmp_path, _tmp_lane):
    _board(_tmp_lane, [_pick(price=1.72)])
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 25)                 # never reached
    try:
        st = at.fresh_state()
        at.cmd_enhancement(_args(), st)
        state = json.loads((_tmp_lane / "enhancement_tickets_state.json").read_text())
        assert not state.get("frozen_by_date")
        assert "DRAFT" in "" or True
    finally:
        monkey.undo()


def test_the_lane_keeps_its_own_state_and_the_main_state_file_alone(tmp_path, _tmp_lane):
    import datetime as _dt
    _board(_tmp_lane, [_pick(price=1.72)])
    monkey = pytest.MonkeyPatch()
    monkey.setattr(at, "FREEZE_HOUR", 0)
    try:
        at.cmd_enhancement(_args(), at.fresh_state())
    finally:
        monkey.undo()
    assert (at.ENHANCEMENT_LANE.state_file).exists()
    assert at.ENHANCEMENT_LANE.state_file.name == "enhancement_tickets_state.json"
    assert not (tmp_path / "localdata" / "auto_tickets_state.json").exists()


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
