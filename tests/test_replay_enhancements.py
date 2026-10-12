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
    assert "live floors" in out
    assert "every market at floor=1.70" in out
    assert "paired bootstrap, B minus A" in out


def test_no_records_is_an_honest_empty_answer(monkeypatch, capsys):
    monkeypatch.setattr(rh, "enh_records", lambda root=None: [])
    assert rh.cmd_enhancements(type("A", (), {"ab": None})()) == 0
    assert "nothing to replay" in capsys.readouterr().out
