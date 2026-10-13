"""Team-under floors derived from settled pick evidence (enh_team_floors).

Synthetic ledgers in tmp_path: a picks file per day plus settled_results.json.
Pins: the floor formula, the no-lookahead cut, the side key, the minimum sample,
that the floor moves with the record, and the gate's verdicts for team legs.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import auto_tickets as at  # noqa: E402
from edgefactory import enh_registry as reg  # noqa: E402
from edgefactory import enh_team_floors as tf  # noqa: E402

DAY = "2026-10-20"


def _ledger(tmp_path: Path, fixtures):
    """fixtures: [(day, home, away, hs, gs, pick_side, [markets])]."""
    (tmp_path / "localdata").mkdir(parents=True, exist_ok=True)
    by_day: dict[str, list] = {}
    results = []
    for day, home, away, hs, gs, side, markets in fixtures:
        results.append({"date": day, "home": home, "away": away, "hs": hs, "gs": gs})
        by_day.setdefault(day, []).append({
            "market": "1x2", "pick": side, "home": home, "away": away,
            "event_notes": [{"market": m, "probability": 0.95} for m in markets]})
    (tmp_path / "localdata" / "settled_results.json").write_text(json.dumps({"rows": results}))
    for day, rows in by_day.items():
        (tmp_path / "localdata" / f"picks_{day}.json").write_text(json.dumps(rows))
    return tmp_path


def _fixtures(n, hits, *, day="2026-10-10", market="home_under_35", side="away", goals=1):
    """n fixtures of `market`; the first `hits` have the home team under the line."""
    out = []
    for i in range(n):
        home_goals = goals if i < hits else 5
        out.append((day, f"Team H{i}", f"Team A{i}", home_goals, 0, side, [market]))
    return out


def test_floor_is_one_over_wilson_lb_plus_margin(tmp_path):
    root = _ledger(tmp_path, _fixtures(40, 38))
    table = tf.team_under_floors(root, DAY)
    entry = table["home_under_35|2"]
    lb = reg.wilson_lb(38, 40)
    assert entry["n"] == 40 and entry["hits"] == 38
    assert entry["floor"] == round(1.0 / lb + reg.ENHANCEMENT_FLOOR_MARGIN, 4)
    assert entry["basis"] == "pick_evidence"


def test_below_minimum_sample_there_is_no_floor(tmp_path):
    root = _ledger(tmp_path, _fixtures(reg.MIN_PRICED_N - 1, reg.MIN_PRICED_N - 1))
    assert tf.team_under_floors(root, DAY) == {}


def test_floor_is_keyed_by_side_and_a_side_without_evidence_has_none(tmp_path):
    root = _ledger(tmp_path, _fixtures(40, 40, side="away"))   # side 2 only
    table = tf.team_under_floors(root, DAY)
    assert "home_under_35|2" in table
    assert "home_under_35|1" not in table


def test_no_lookahead_rows_dated_on_or_after_the_day_are_excluded(tmp_path):
    root = _ledger(tmp_path, _fixtures(40, 40, day=DAY))       # all dated the derived day
    assert tf.team_under_floors(root, DAY) == {}
    assert "home_under_35|2" in tf.team_under_floors(root, "2026-10-21")


def test_the_floor_moves_with_the_record(tmp_path):
    root = _ledger(tmp_path, _fixtures(40, 40))
    before = tf.team_under_floors(root, DAY)["home_under_35|2"]["floor"]
    root = _ledger(tmp_path, _fixtures(40, 40, day="2026-10-10") +
                   _fixtures(40, 20, day="2026-10-11"))
    after = tf.team_under_floors(root, DAY)["home_under_35|2"]["floor"]
    assert after > before


def test_a_team_under_leg_fires_only_at_or_above_its_side_floor():
    table = {"home_under_35|2": {"floor": 1.13, "n": 344, "hits": 340,
                                 "wilson_lb": 0.9705, "basis": "pick_evidence"}}
    pick = {"home": "H", "away": "A", "match": "H vs A", "date": DAY, "pick": "away",
            "bucket": "CERTIFIED_CLEAN", "rule": "r1", "recommended_enhancement": "home_under_35",
            "enhancement_label": "Home Under 3.5", "enhancement_probability": 0.96,
            "enhancement_price_book": "b", "enhancement_price_source": "oddspapi"}
    below = at.enhancement_legs([{**pick, "enhancement_price": 1.12}], team_floors=table)[0]
    at_floor = at.enhancement_legs([{**pick, "enhancement_price": 1.13,
                                     "enhancement_consensus_price": 1.13}], team_floors=table)[0]
    assert below["verdict"] == "below_floor"
    assert at_floor["verdict"] == "fire"
    assert at_floor["floor_basis"] == "pick_evidence"


def test_a_team_under_leg_on_a_side_without_evidence_does_not_fire():
    table = {"home_under_35|2": {"floor": 1.13, "n": 344, "hits": 340,
                                 "wilson_lb": 0.9705, "basis": "pick_evidence"}}
    pick = {"home": "H", "away": "A", "match": "H vs A", "date": DAY, "pick": "home",
            "bucket": "CERTIFIED_CLEAN", "rule": "r1", "recommended_enhancement": "home_under_35",
            "enhancement_label": "Home Under 3.5", "enhancement_probability": 0.96,
            "enhancement_price": 3.00, "enhancement_price_book": "b",
            "enhancement_price_source": "oddspapi"}
    leg = at.enhancement_legs([pick], team_floors=table)[0]
    assert leg["verdict"] == "no_floor"
    assert leg["floor"] is None


def _team_pick(price, consensus, *, market="away_under_25", side="away"):
    return {"home": "H", "away": "A", "match": "H vs A", "date": DAY, "pick": side,
            "bucket": "CERTIFIED_CLEAN", "rule": "r1", "recommended_enhancement": market,
            "enhancement_label": "Away Under 2.5", "enhancement_probability": 0.92,
            "enhancement_price": price, "enhancement_price_book": "b",
            "enhancement_price_source": "oddspapi",
            "enhancement_consensus_price": consensus}


def test_a_best_quote_the_median_does_not_support_is_not_a_bet():
    table = {"away_under_25|2": {"floor": 1.20, "n": 900, "hits": 830,
                                 "wilson_lb": 0.9, "basis": "pick_evidence"}}
    leg = at.enhancement_legs([_team_pick(1.90, 1.14)], team_floors=table)[0]
    assert leg["verdict"] == "outlier_price"


def test_a_price_the_median_also_supports_fires():
    table = {"away_under_25|2": {"floor": 1.20, "n": 900, "hits": 830,
                                 "wilson_lb": 0.9, "basis": "pick_evidence"}}
    leg = at.enhancement_legs([_team_pick(1.68, 1.50)], team_floors=table)[0]
    assert leg["verdict"] == "fire"


def test_a_team_leg_with_no_consensus_quote_does_not_fire():
    table = {"away_under_25|2": {"floor": 1.20, "n": 900, "hits": 830,
                                 "wilson_lb": 0.9, "basis": "pick_evidence"}}
    leg = at.enhancement_legs([_team_pick(1.68, None)], team_floors=table)[0]
    assert leg["verdict"] == "outlier_price"


def test_a_swapped_fixture_reads_the_feed_team_it_names():
    from edgefactory.enh_pricing import attach_enhancement_price, norm_team
    nh, na = norm_team("Feed Home"), norm_team("Feed Away")
    index = {"pairs": {(nh, na): {("tt_home_2.5", "under"): (1.5, "b", "t", "oddspapi"),
                                  ("tt_away_2.5", "under"): (1.1, "b", "t", "oddspapi")}},
             "spread": {}, "names": {(nh, na): ("Feed Home", "Feed Away")}, "quotes": {}}
    pick = {"home": "Feed Away", "away": "Feed Home", "pick": "home",
            "recommended_enhancement": "home_under_25", "enhancement_probability": 0.9}
    out = attach_enhancement_price(pick, index, match_fn=lambda a, b: norm_team(a) == norm_team(b))
    # our home team is the feed's AWAY team, so its under 2.5 is the feed's tt_away_2.5 quote
    assert out["enhancement_price"] == 1.1
