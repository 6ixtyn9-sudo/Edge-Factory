"""Home-fade price-robustness study — contracts pinned here.

1. Price-source selection is EXPLICIT: fb (production fade price, the view's
   pick_odds), zb (independent capture), best/worst = max/min of the quotes
   actually on the row, mid = harmonic mean (average implied probability).
   Missing quotes stay None; nothing inherits a price.
2. Haircuts and conservative pricing are exact: roi_scale multiplies the
   final roi; adjust_k changes WINNER payouts only (losers still lose 1).
3. Odds bands are half-open; caps drop above-priced rows and COUNT them.
4. Outlier removal recomputes roi without the top-1/2/3 winning profits;
   small samples degrade to None, never to fake numbers.
5. Month/league/band contributions partition pnl exactly; distinct winning
   events/leagues count what they say.
6. Windows stay disjoint; outcome never affects pricing, membership or
   day counts — only grading.
7. ROI/Wilson arithmetic is hand-checkable; the gate-feasibility analysis
   proves impossibility when hit <= threshold and finds the exact n when
   hit > threshold; bootstrap is seeded and deterministic.
8. Predeclared search parameters (threshold ladder, bands, sources, caps)
   keep their recorded counts — the study stays finite and reproducible.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory import fade_research as fr
from edgefactory.config import BEST_ODDS_HAIRCUT

SPLIT = "2025-06-01"
CONFIRM = "2026-01-01"
C65 = fr.Candidate(65, (fr.HOME_FADE_CONDITION,))


def mk_row(**kw):
    row = {
        "date": "2025-01-10",
        "home": "A",
        "away": "B",
        "outcome": "home",
        "parent_pick": "away",
        "pick": "home",
        "ml_p": 0.70,
        "fb_odds": 8.0,
        "zb_odds": 9.0,
        "parent_pick_odds": 1.3,
        "league": "epl",
        "league_canonical": "epl",
        "comp_type_pre": "league",
    }
    row.update(kw)
    # mirror the settled-view shape: the view's pick_odds IS the fb quote
    row["pick_odds"] = kw.get("pick_odds", row["fb_odds"])
    return row


def matched(rows):
    return [r for r in rows if C65.matches(r)]


# --------------------------------------------------------------------------
# 1. Price-source selection
# --------------------------------------------------------------------------
def test_price_sources_are_explicit_and_independent():
    r = mk_row(fb_odds=8.0, zb_odds=9.0)
    assert fr.price_of(r, "fb") == 8.0
    assert fr.price_of(r, "zb") == 9.0
    assert fr.price_of(r, "best") == 9.0
    assert fr.price_of(r, "worst") == 8.0
    # mid is the harmonic mean = average implied probability
    assert fr.price_of(r, "mid") == pytest.approx(2 / (1 / 8 + 1 / 9), abs=1e-9)


def test_price_source_missing_quotes_never_invented():
    r = mk_row(fb_odds=None, zb_odds=9.0)
    assert fr.price_of(r, "fb") is None
    assert fr.price_of(r, "zb") == 9.0
    assert fr.price_of(r, "best") == 9.0  # best of the AVAILABLE quotes
    assert fr.price_of(r, "worst") == 9.0
    both_none = mk_row(fb_odds=None, zb_odds=None)
    for s in fr.PRICE_SOURCES:
        assert fr.price_of(both_none, s) is None
    with pytest.raises(ValueError):
        fr.price_of(r, "pinny")


def test_fb_source_falls_back_to_view_pick_odds():
    # production view rows carry the fb quote as pick_odds without fb_odds
    r = {"pick_odds": 7.5}
    assert fr.price_of(r, "fb") == 7.5
    assert fr.price_of(r, "zb") is None
    assert fr.price_of(r, "best") == 7.5
    # fb_odds explicit beats the fallback (study loader carries both)
    r2 = {"pick_odds": 7.5, "fb_odds": float("nan")}
    assert fr.price_of(r2, "fb") == 7.5  # NaN is not a usable quote


# --------------------------------------------------------------------------
# 2. ROI accounting, haircuts and conservative pricing
# --------------------------------------------------------------------------
def test_pnl_stats_hand_computed():
    rows = matched(
        [
            mk_row(fb_odds=8.0),  # win  +7
            mk_row(outcome="away", fb_odds=6.0),  # loss -1
            mk_row(outcome="away", fb_odds=None),
        ]
    )  # unpriced
    s = fr.pnl_stats(rows, "fb")
    assert s["n"] == 3 and s["n_priced"] == 2 and s["n_unpriced"] == 1
    assert s["wins"] == 1 and s["hit"] == round(1 / 3, 4)
    assert s["pnl"] == 6.0 and s["roi"] == 3.0 and s["roi_raw"] == 3.0
    assert s["avg_odds"] == 7.0 and s["median_odds"] == 7.0
    assert s["winner_odds"] == {"n": 1, "avg": 8.0, "max": 8.0}
    assert s["loser_odds"] == {"n": 1, "avg": 6.0}
    assert s["n_days"] == 1


def test_roi_scale_haircuts():
    rows = matched([mk_row(fb_odds=8.0), mk_row(outcome="away", fb_odds=6.0)])
    s = fr.pnl_stats(rows, "fb", roi_scale=BEST_ODDS_HAIRCUT)
    assert s["roi_raw"] == 3.0 and s["roi"] == 1.5  # repo 0.5 haircut
    s25 = fr.pnl_stats(rows, "fb", roi_scale=fr.CONSERVATIVE_ROI_SCALE)
    assert s25["roi"] == 0.75  # harsher 0.25 haircut
    # hit / n are properties of the slice, not of the haircut
    assert s25["hit"] == s["hit"] == 0.5 and s25["n_priced"] == 2


def test_price_adjust_changes_winner_payout_only():
    rows = matched(
        [
            mk_row(fb_odds=9.0),  # win at o'=1+8*0.5 -> +4
            mk_row(outcome="away", fb_odds=9.0),
        ]
    )  # loss still -1
    s = fr.pnl_stats(rows, "fb", adjust_k=fr.PRICE_ADJUST_K)
    assert s["pnl"] == 3.0 and s["roi"] == 1.5
    assert s["avg_odds"] == 9.0  # avg_odds reports the QUOTE, transform is for pnl


# --------------------------------------------------------------------------
# 3. Odds bands, caps and filtered-row accounting
# --------------------------------------------------------------------------
def test_band_and_cap_drop_and_count_rows():
    rows = matched(
        [mk_row(fb_odds=4.9), mk_row(fb_odds=5.0), mk_row(fb_odds=9.9), mk_row(fb_odds=12.0)]
    )
    band = fr.pnl_stats(rows, "fb", band=(5.0, 10.0))
    assert band["n"] == 2 and band["n_filtered"] == 2  # half-open [5, 10)
    cap = fr.pnl_stats(rows, "fb", cap=10.0)
    assert cap["n"] == 3 and cap["n_filtered"] == 1  # 12.0 dropped
    assert fr.pnl_stats(rows, "fb", cap=12.0)["n_filtered"] == 0  # cap inclusive
    combined = fr.pnl_stats(rows, "fb", cap=10.0, band=(2.0, 5.0))
    assert combined["n"] == 1 and combined["n_filtered"] == 3


def test_unpriced_rows_survive_odds_filters():
    rows = matched([mk_row(fb_odds=None, zb_odds=None), mk_row(fb_odds=50.0)])
    s = fr.pnl_stats(rows, "fb", cap=10.0)
    # the unpriced row is NOT filtered (no price to judge) but never earns roi
    assert s["n"] == 1 and s["n_priced"] == 0 and s["n_filtered"] == 1


# --------------------------------------------------------------------------
# 4. Outlier-win removal
# --------------------------------------------------------------------------
def _priced_winners():
    return matched(
        [
            mk_row(fb_odds=11.0, date="2025-01-01"),  # +10
            mk_row(fb_odds=6.0, date="2025-01-02"),  # +5
            mk_row(fb_odds=4.0, date="2025-01-03"),  # +3
            mk_row(outcome="away", fb_odds=5.0, date="2025-01-04"),  # -1
            mk_row(outcome="away", fb_odds=7.0, date="2025-01-05"),  # -1
        ]
    )


def test_top_k_removal_exact_math():
    s = fr.pnl_stats(_priced_winners(), "fb")
    k = fr.concentration(s["rows_priced"])
    assert k["n_priced"] == 5 and k["pnl_total"] == 16.0 and k["roi"] == 3.2
    assert k["roi_wo_top1"] == round((16 - 10) / 4, 4)  # 1.5
    assert k["roi_wo_top2"] == round((16 - 15) / 3, 4)
    assert k["roi_wo_top3"] == round((16 - 18) / 2, 4) == -1.0
    assert k["median_bet_return"] == 3.0  # median of [-1, -1, 3, 5, 10]
    assert k["top_wins"] == [10.0, 5.0, 3.0]
    assert k["n_winners"] == 3 and k["distinct_win_events"] == 3
    assert k["distinct_win_leagues"] == 1 and k["distinct_leagues"] == 1


def test_top_k_removal_small_samples_degrade_safely():
    s = fr.pnl_stats(matched([mk_row(fb_odds=3.0)]), "fb")
    k = fr.concentration(s["rows_priced"])
    assert k["roi_wo_top1"] is None and k["roi_wo_top2"] is None
    assert fr.concentration([])["roi"] is None


# --------------------------------------------------------------------------
# 5. Month/league/band concentration partitions
# --------------------------------------------------------------------------
def test_contributions_partition_pnl_and_count_distinct():
    rows = _priced_winners()
    rows[1]["league_canonical"] = "it1"
    s = fr.pnl_stats(rows, "fb")
    months = fr.contribution_by(s["rows_priced"], fr.month_key)
    assert [m["key"] for m in months] == ["2025-01"]  # all one month
    assert abs(sum(m["pnl"] for m in months) - 16.0) < 1e-9
    assert abs(sum(m["pnl_share"] for m in months) - 1.0) < 1e-9
    leagues = fr.contribution_by(s["rows_priced"], fr.league_key)
    assert {lg["key"] for lg in leagues} == {"epl", "it1"}
    bands = fr.contribution_by(s["rows_priced"], fr.band_key())
    assert {b["key"] for b in bands} == {"3-5", "5-10", "10+"}
    assert abs(sum(b["pnl"] for b in bands) - 16.0) < 1e-9


def test_month_and_quarter_keys():
    assert fr.month_key(mk_row(date="2026-03-09"), 5.0) == "2026-03"
    assert fr.quarter_key(mk_row(date="2026-03-09"), 5.0) == "2026Q1"
    assert fr.quarter_key(mk_row(date="2026-12-31"), 5.0) == "2026Q4"
    rows = matched([mk_row(date="2025-01-15", fb_odds=4.0), mk_row(date="2025-02-15", fb_odds=4.0)])
    quarters = fr.contribution_by(fr.pnl_stats(rows, "fb")["rows_priced"], fr.quarter_key)
    assert len(quarters) == 1 and quarters[0]["n_days"] == 2


# --------------------------------------------------------------------------
# 6. Windows disjoint; outcome never touches pricing/membership
# --------------------------------------------------------------------------
def test_window_separation_in_by_window():
    rows = matched(
        [
            mk_row(date="2025-05-31"),
            mk_row(date="2025-06-01"),
            mk_row(date="2026-01-01"),
            mk_row(date="2026-03-01"),
        ]
    )
    w = fr.by_window(rows, "fb", SPLIT, CONFIRM)
    assert w["train"]["n"] == 1 and w["valid"]["n"] == 1 and w["confirm"]["n"] == 2
    assert sum(w[k]["n"] for k in w) == 4


def test_outcome_never_changes_pricing_or_membership():
    a = mk_row(outcome="home")
    b = mk_row(outcome="away")  # same quotes, different result
    for src in fr.PRICE_SOURCES:
        assert fr.price_of(a, src) == fr.price_of(b, src)
    rows = matched([a, dict(b, date="2025-01-11")])
    s = fr.pnl_stats(rows, "fb")
    # count-based fields are outcome-independent; only wins/pnl react
    same_again = fr.pnl_stats(
        matched([mk_row(outcome="away"), mk_row(outcome="away", date="2025-01-11")]), "fb"
    )
    assert (s["n"], s["n_priced"], s["n_days"], s["avg_odds"]) == (
        same_again["n"],
        same_again["n_priced"],
        same_again["n_days"],
        same_again["avg_odds"],
    )
    assert s["wins"] != same_again["wins"]
    # home/away/odds/league/date only: results dict lists exactly the allowed keys
    assert set(s["price"]) == {"source", "adjust_k", "cap", "band", "roi_scale"}


# --------------------------------------------------------------------------
# 7. Book-vs-parity, Wilson math, bootstrap
# --------------------------------------------------------------------------
def test_pnl_stats_matches_grade_rows_accounting():
    rows = matched(
        [
            mk_row(),
            mk_row(outcome="away", date="2025-02-01", fb_odds=4.0),
            mk_row(fb_odds=None, date="2025-03-01"),
        ]
    )
    g = fr.grade_rows(rows, C65, SPLIT, CONFIRM)["train"]
    s = fr.pnl_stats(rows, "fb")
    assert (
        g["n"],
        g["n_priced"],
        g["wins"],
        g["roi"],
        g["avg_odds"],
        g["wilson_lb"],
        g["n_days"],
    ) == (s["n"], s["n_priced"], s["wins"], s["roi"], s["avg_odds"], s["wilson_lb"], s["n_days"])


def test_wilson_gate_impossible_when_hit_below_threshold():
    wg = fr.wilson_gate_analysis(0.244, 197)
    assert wg["required_n"] is None
    assert "impossible" in wg["impossible_reason"] or "no finite n" in wg["impossible_reason"]
    assert wg["wilson_lb"] == pytest.approx(0.189, abs=1e-3)
    # gate would need hit 0.574 at this n -> prices <= 1.74 to be fair
    assert wg["required_hit_at_n"] == pytest.approx(0.5736, abs=1e-3)
    assert wg["fair_odds_ceiling_for_gate"] == pytest.approx(1.743, abs=1e-3)


def test_wilson_gate_exact_n_when_hit_above_threshold():
    wg = fr.wilson_gate_analysis(0.60, 40)
    assert wg["required_n"] == 96  # exact: the first n clearing the gate
    from edgefactory.assay import wilson_lb

    assert wilson_lb(round(0.60 * 96), 96) >= 0.5
    assert wilson_lb(round(0.60 * 95), 95) < 0.5


def test_empty_everything_is_safe():
    s = fr.pnl_stats([], "fb")
    assert s["n"] == 0 and s["roi"] is None and s["hit"] == 0.0
    assert s["wilson_lb"] == 0.0 and s["avg_odds"] is None
    assert fr.bootstrap_roi_ci([])["ci_lo"] is None
    assert fr.implied_baseline([])["avg_implied_prob"] is None
    wg = fr.wilson_gate_analysis(0.0, 0)
    assert wg["required_hit_at_n"] is None and wg["required_n"] is None


def test_implied_baseline_math():
    rows = [mk_row(fb_odds=4.0), mk_row(fb_odds=2.0, outcome="away")]
    s = fr.pnl_stats(rows, "fb")
    im = fr.implied_baseline(s["rows_priced"])
    assert im["n_priced"] == 2
    assert im["avg_implied_prob"] == pytest.approx((0.25 + 0.5) / 2, abs=1e-3)
    assert im["observed_hit"] == pytest.approx(0.5, abs=1e-3)
    assert im["hit_minus_implied"] == pytest.approx(0.125, abs=1e-3)


def test_bootstrap_deterministic_and_honest_on_all_losses():
    pnls = [9.0, -1.0, -1.0, 4.0, -1.0]
    a = fr.bootstrap_roi_ci(pnls)
    b = fr.bootstrap_roi_ci(pnls)
    assert a == b  # seeded -> reproducible
    assert a["seed"] == 42 and a["n_boot"] == 10_000
    assert a["point"] == pytest.approx(sum(pnls) / len(pnls), abs=1e-9)
    hopeless = fr.bootstrap_roi_ci([-1.0] * 30)
    assert hopeless["ci_hi"] == -1.0 and hopeless["p_positive"] == 0.0


# --------------------------------------------------------------------------
# 8. Predeclared parameters keep recorded counts
# --------------------------------------------------------------------------
def test_predeclared_search_parameters():
    assert fr.PRICE_STUDY_THRESHOLDS == (55, 60, 65, 70, 75, 80)
    assert len(fr.PRICE_STUDY_BANDS) == 5
    assert fr.PRICE_STUDY_BANDS[0] == (1.20, 2.00) and fr.PRICE_STUDY_BANDS[-1][0] == 10.00
    assert fr.PRICE_SOURCES == ("fb", "zb", "best", "worst", "mid")
    assert fr.ODDS_CAPS == (5.0, 10.0, 20.0)
    assert fr.PRIMARY_STUDY_THRESHOLD == 65
    assert fr.CONSERVATIVE_ROI_SCALE == 0.25
    assert fr.PRICE_ADJUST_K == 0.5
    ladder = [fr.Candidate(t, (fr.HOME_FADE_CONDITION,)) for t in fr.PRICE_STUDY_THRESHOLDS]
    names = [c.name() for c in ladder]
    assert names[2] == "ml-fade home-fade avg_p>=65"
    assert len(set(names)) == 6
