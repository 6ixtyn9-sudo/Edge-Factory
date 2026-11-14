"""`replay_harness --enhancements`: floor variants on the settled registry.

The harness's own doctrine applies unchanged: relative comparisons only, every
output prints n, cells under 30 are flagged, and the primary metric is MEAN LOG
GROWTH PER BET-DAY (final bank is one lucky path). The enhancement replay reads
the settled registry rather than the acca universe, and reuses the harness's
paired day-resampler rather than growing a second bootstrap.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
import replay_harness as rh  # noqa: E402

FLOORS = {"match_over_25": 1.60, "btts_yes": 1.85}


def _rec(market="match_over_25", date="2026-10-12", price=1.72, hit=True,
         bucket="", rule="", match="", stated=None):
    return {"market": market, "date": date, "price": price, "hit": hit,
            "bucket": bucket, "rule": rule, "source": "oddspapi",
            "match": match, "stated": stated}


def test_enh_records_flattens_the_registry(tmp_path):
    (tmp_path / "localdata").mkdir()
    (tmp_path / "localdata" / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {"match_over_25@v1": {
            "status": "PAPER", "records": [
                {"date": "2026-08-03", "match": "A vs B", "price": 1.9, "hit": True,
                 "bucket": "CERTIFIED_CLEAN", "rule": "r1", "source": "s"},
                {"date": "2026-08-04", "match": "C vs D", "price": 1.5, "hit": False},
            ]}}}))
    rows = rh.enh_records(tmp_path)
    assert [r["market"] for r in rows] == ["match_over_25"] * 2
    assert rows[0]["bucket"] == "CERTIFIED_CLEAN" and rows[1]["bucket"] == ""
    # junk prices are never a settled outcome
    (tmp_path / "localdata" / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {"m@v1": {"records": [
            {"date": "d", "price": 1.0, "hit": True},
            {"date": "d", "price": "1.9", "hit": True},
            {"date": "d", "price": None, "hit": True}], "status": "PAPER"}}}))
    assert rh.enh_records(tmp_path) == []


def test_the_floor_is_the_only_gate_on_a_settled_leg():
    records = [_rec(price=1.59, match="A vs B"), _rec(price=1.60, match="C vs D"),
               _rec(price=1.72, match="E vs F")]
    days = rh.enh_day_growth(records, {"match_over_25": 1.60})
    # 1.59 does not fire; 1.60 and 1.72 pair into ONE bet-day acca
    assert days["2026-10-12"]["bets"] == 1
    assert days["2026-10-12"]["hits"] == 1
    # a market with no floor never fires
    assert rh.enh_day_growth(records, {}) == {}
    assert rh.enh_day_growth([_rec(market="away_under_35", price=1.02)], FLOORS) == {}


def test_a_lone_firing_leg_is_a_no_bet_day_not_a_single():
    assert rh.enh_day_growth([_rec(price=1.72)], {"match_over_25": 1.60}) == {}


def test_the_acca_card_prices_the_day_the_way_the_lane_would():
    stake = at.ENHANCEMENT_LANE.stake_frac       # 25% of free bank per bet-day
    f = stake / 2                                # MAX_ACCAS: the lane's split
    records = [_rec(price=2.00, hit=True, match="A vs B"),
               _rec(price=2.00, hit=True, match="C vs D")]
    day = rh.enh_day_growth(records, FLOORS)["2026-10-12"]
    # one acca, both legs home, odds 2.00 x 2.00 — the whole day's stake rides
    assert (day["bets"], day["hits"]) == (1, 1)
    assert day["growth"] == pytest.approx(1.0 + f * (4.00 - 1.0))
    assert day["log_growth"] == pytest.approx(math.log(day["growth"]))
    # one leg missing loses the acca: the day keeps the whole -f
    lost = rh.enh_day_growth([_rec(price=2.00, hit=True, match="A vs B"),
                              _rec(price=2.00, hit=False, match="C vs D")],
                             FLOORS)["2026-10-12"]
    assert (lost["bets"], lost["hits"]) == (1, 0)
    assert lost["growth"] == pytest.approx(1.0 - f)


def test_record_outcome_stores_the_cohort_rate_and_nothing_else_stated(tmp_path):
    from edgefactory.enh_registry import record_outcome, registry_path
    record_outcome(tmp_path, date_="2026-10-14", match="A vs B", market="match_over_25",
                   price=1.50, hit=True, cohort_rate=0.6214)
    record_outcome(tmp_path, date_="2026-10-14", match="C vs D", market="match_over_25",
                   price=1.50, hit=False, cohort_rate=1.7)   # not a rate: stored as None
    recs = json.loads(registry_path(tmp_path).read_text())["markets"]["match_over_25@v1"]["records"]
    assert [r["cohort_rate"] for r in recs] == [0.6214, None]


def test_replay_reads_the_cohort_rate_as_its_ranking_input(tmp_path):
    (tmp_path / "localdata").mkdir()
    (tmp_path / "localdata" / "enhancement_registry.json").write_text(json.dumps({
        "version": 2, "markets": {"match_over_25@v1": {"status": "PAPER", "records": [
            {"date": "2026-10-14", "match": "A vs B", "price": 1.5, "hit": True,
             "cohort_rate": 0.62},
            {"date": "2026-10-14", "match": "C vs D", "price": 1.5, "hit": True}]}}}))
    rows = rh.enh_records(tmp_path)
    assert sorted((r["cohort_rate"] is None, r["cohort_rate"] or 0.0) for r in rows) == \
        [(False, 0.62), (True, 0.0)]


def test_stake_fraction_and_mode_reach_the_enhancement_card():
    records = [_rec(price=2.00, hit=True, match="A vs B"),
               _rec(price=2.00, hit=True, match="C vs D")]
    # one acca: per_acca sizing risks f / MAX_ACCAS of the bank on the day
    small = rh.enh_day_growth(records, FLOORS, stake_frac=0.10)["2026-10-12"]
    big = rh.enh_day_growth(records, FLOORS, stake_frac=0.25)["2026-10-12"]
    assert small["growth"] == pytest.approx(1.0 + (0.10 / at.MAX_ACCAS) * 3.0)
    assert big["growth"] == pytest.approx(1.0 + (0.25 / at.MAX_ACCAS) * 3.0)
    assert big["log_growth"] > small["log_growth"]
    # per_day risks the full fraction on the day
    pd = rh.enh_day_growth(records, FLOORS, stake_frac=0.10,
                           stake_mode="per_day")["2026-10-12"]
    assert pd["growth"] == pytest.approx(1.0 + 0.10 * 3.0)


def test_stake_only_spec_moves_the_stake_and_the_report_sweeps_it(tmp_path, monkeypatch, capsys):
    records = [_rec(date=f"2026-09-{d:02d}", price=1.50 + 0.05 * d, hit=(d % 2 == 0),
                    match=f"Home{d} vs Away{d}") for d in range(1, 11)]
    records += [_rec(date=f"2026-09-{d:02d}", price=1.50 + 0.05 * d, hit=True,
                     match=f"City{d} vs Town{d}") for d in range(1, 11)]
    monkeypatch.setattr(rh, "enh_records", lambda root=None: records)
    args = type("A", (), {"ab": ("stake_frac=0.10", "stake_frac=0.25")})()
    assert rh.cmd_enhancements(args) == 0
    out = capsys.readouterr().out
    assert "arm A: live (MIN_LEG_ODDS) | stake_frac=0.1" in out
    assert "arm B: live (MIN_LEG_ODDS) | stake_frac=0.25" in out
    assert "stake sweep" in out and "<- live" in out
    # the two stake-only arms gate identically: same bet-days and bets
    a = rh.enh_arm(records, rh._root_floors(records), stake_frac=0.10)
    b = rh.enh_arm(records, rh._root_floors(records), stake_frac=0.25)
    assert (a["days"], a["bets"], a["hits"]) == (b["days"], b["bets"], b["hits"])
    assert a["mean_log_growth"] != b["mean_log_growth"]


def test_enh_arm_reports_the_harnesss_primary_metric():
    records = [_rec(date="2026-10-12", price=2.00, hit=True, match="A vs B"),
               _rec(date="2026-10-12", price=2.00, hit=True, match="C vs D"),
               _rec(date="2026-10-13", price=2.00, hit=True, match="E vs F"),
               _rec(date="2026-10-13", price=2.00, hit=False, match="G vs H")]
    arm = rh.enh_arm(records, FLOORS)
    assert (arm["days"], arm["bets"], arm["hits"]) == (2, 2, 1)
    assert arm["rate"] == pytest.approx(0.5)
    assert arm["mean_log_growth"] == pytest.approx(
        sum(arm["by_day"].values()) / 2)


def test_noise_flag_and_the_paired_resampler_are_the_harnesss_own():
    assert rh.noise_flag(29).strip() == "⚠ small-n"
    assert rh.noise_flag(30) == ""
    # identical arms => the resampler must find nothing (the 2026-09-04 bug
    # printed a ±22,000% interval for two identical variants)
    ga = {"2026-10-12": 0.01, "2026-10-13": -0.02, "2026-10-14": 0.005}
    bs = rh._paired_day_bootstrap(dict(ga), dict(ga), sorted(ga), n=200)
    assert bs["median"] == pytest.approx(0.0)
    assert bs["p10"] == pytest.approx(0.0) and bs["p90"] == pytest.approx(0.0)


def test_the_report_runs_on_a_registry_and_flags_small_n(tmp_path, monkeypatch, capsys):
    records = [_rec(date=f"2026-09-{d:02d}", price=1.72, hit=(d % 3 != 0))
               for d in range(1, 6)]
    monkeypatch.setattr(rh, "enh_records", lambda root=None: records)
    args = type("A", (), {"ab": None})()
    assert rh.cmd_enhancements(args) == 0
    out = capsys.readouterr().out
    assert "ENHANCEMENT LANE REPLAY" in out
    assert "RELATIVE floor comparisons" in out
    assert "mean log growth/bet-day" in out
    assert "⚠ small-n" in out            # n=5 bets: the harness flags it
    assert "match_over_25" in out


def test_the_report_compares_two_uniform_floor_variants(tmp_path, monkeypatch, capsys):
    # two fixtures a day: the lane's card needs a partner before it bets
    records = [_rec(date=f"2026-09-{d:02d}", price=1.50 + 0.05 * d,
                    hit=(d % 2 == 0), match=f"Home{d} vs Away{d}") for d in range(1, 11)]
    records += [_rec(date=f"2026-09-{d:02d}", price=1.50 + 0.05 * d, hit=True,
                     match=f"City{d} vs Town{d}") for d in range(1, 11)]
    monkeypatch.setattr(rh, "enh_records", lambda root=None: records)
    args = type("A", (), {"ab": ("live", "floor=1.70")})()
    assert rh.cmd_enhancements(args) == 0
    out = capsys.readouterr().out
    assert "live (MIN_LEG_ODDS)" in out
    assert "every market at floor=1.70" in out
    assert "paired bootstrap, B minus A" in out


def test_uniform_arm_gates_on_its_own_floor_not_the_static_table():
    # Two priced 1.40 over-2.5 legs on one day: the static table (1.60) would
    # block them, so a 1.30 arm must bet and a 1.60 arm must not.
    records = [_rec(price=1.40, hit=True, match="A vs B"),
               _rec(price=1.40, hit=True, match="C vs D")]
    assert rh.enh_day_growth(records, {"match_over_25": 1.30})["2026-10-12"]["bets"] == 1
    assert rh.enh_day_growth(records, {"match_over_25": 1.60}) == {}
    # and the two uniform arms must differ, or the replay is blind to the floor
    lo = rh.enh_arm(records, {"match_over_25": 1.00})
    hi = rh.enh_arm(records, {"match_over_25": 1.60})
    assert lo["bets"] == 1 and hi["bets"] == 0


def test_live_arm_is_the_shared_minimum_on_every_market():
    records = [_rec(market="match_over_25", price=1.40),
               _rec(market="away_under_35", price=1.35)]
    assert rh._root_floors(records) == {"away_under_35": at.MIN_LEG_ODDS,
                                        "match_over_25": at.MIN_LEG_ODDS}


def test_derive_floors_honours_its_parent_table_and_defaults_to_static():
    from edgefactory import enh_registry as er
    # one priced record: below the evidence minimum, so the market inherits its parent
    reg = {"version": 2, "markets": {"match_over_25@v1": {"status": "PAPER", "records": [
        {"date": "2026-10-01", "match": "A vs B", "price": 1.5, "hit": True}]}}}
    out = er.derive_floors(reg, "2026-10-13", parent_floors={"match_over_25": 1.30},
                           margin=er.ENHANCEMENT_FLOOR_MARGIN)
    assert out["floors"]["match_over_25"]["floor"] == 1.30
    assert er.floor_for_slice({}, "match_over_25", parent_floors={"match_over_25": 1.30}) \
        == (1.30, "inherited")
    # no parent argument: the operator's static table, unchanged for live callers
    assert er.floor_for_slice({}, "match_over_25") == (1.60, "inherited")


def test_no_records_is_an_honest_empty_answer(monkeypatch, capsys):
    monkeypatch.setattr(rh, "enh_records", lambda root=None: [])
    assert rh.cmd_enhancements(type("A", (), {"ab": None})()) == 0
    assert "nothing to replay" in capsys.readouterr().out


@pytest.mark.parametrize('losing_fixtures', [(), ('Team0 vs Opp0',),
                                          ('Team0 vs Opp0', 'Team1 vs Opp1',
                                           'Team2 vs Opp2', 'Team3 vs Opp3')])
@pytest.mark.parametrize('mode, weights', [('per_acca', None), ('per_day', '2,1')])
def test_simultaneous_ticket_pnl_adds_like_live_settlement(monkeypatch, losing_fixtures, mode, weights):
    # Force two tickets so a multiplicative error cannot hide in a one-ticket test.
    monkeypatch.setattr(at, 'ENH_MAX_ACCAS', 2)
    records = [_rec(price=2., hit=f'Team{i} vs Opp{i}' not in losing_fixtures,
                    match=f'Team{i} vs Opp{i}') for i in range(4)]
    saved = []
    actual_plan_day = at.plan_day

    def spy(*a, **kw):
        plan = actual_plan_day(*a, **kw)
        saved.extend(plan)
        return plan

    monkeypatch.setattr(at, 'plan_day', spy)
    day = rh.enh_day_growth(records, FLOORS, stake_frac=.25,
                           stake_mode=mode, weights=weights)['2026-10-12']
    assert len(saved) == day['bets'] == 2
    # Independent cash accounting: both tickets funded from opening bank 100.
    staked = sum(a['stake_pct'] for a in saved)
    returned = sum(a['stake_pct'] * a['odds'] for a in saved
                   if all(l['match'] not in losing_fixtures for l in a['legs']))
    assert day['growth'] == pytest.approx((100 - staked + returned)/100)
    assert day['log_growth'] == pytest.approx(math.log(day['growth']))
    if not losing_fixtures:
        assert day['growth'] == pytest.approx(1.75)
        assert day['growth'] != pytest.approx(1.375**2)


def test_live_replay_floor_gates_match_the_current_lane_on_all_mapped_markets():
    # The live floor already matches MIN_LEG_ODDS; derived floors are a variant,
    # not a drift repair. Do not reintroduce static floors or ceilings here.
    from enhancement_fixtures import with_evidence
    from edgefactory.enh_pricing import MARKET_PRICE_MAP
    for market, mapping in MARKET_PRICE_MAP.items():
        if not mapping:
            continue
        for price in (1.29, 1.30, 1.40, 4.50):
            records = [_rec(market=market, price=price, match='A vs B')]
            floors = rh._root_floors(records)
            fired = bool(rh._firing_by_day(records, floors))
            live = at.enhancement_legs([with_evidence({'recommended_enhancement': market,
                                         'enhancement_probability': .6,
                                         'enhancement_price': price})])[0]
            assert fired == (live['verdict'] == 'fire')
