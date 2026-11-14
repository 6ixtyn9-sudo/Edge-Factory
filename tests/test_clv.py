from edgefactory.clv import (
    beat_later_price,
    build_pick_id,
    implied_prob_delta,
    odds_to_implied_prob,
    raw_odds_delta,
    summarize_clv,
)


def test_build_pick_id_is_stable():
    pick_id = build_pick_id(
        "2026-06-17",
        "Arsenal",
        "Chelsea",
        "1x2",
        "home",
        "3way-unanimous avg_p>=65",
    )
    assert pick_id == "2026-06-17|arsenal|chelsea|1x2|home|3way-unanimous-avg-p-65"


def test_odds_to_implied_prob():
    assert odds_to_implied_prob(None) is None
    assert odds_to_implied_prob(1.0) is None
    assert abs(odds_to_implied_prob(2.0) - 0.5) < 1e-9


def test_raw_odds_delta():
    assert raw_odds_delta(None, 1.8) is None
    assert abs(raw_odds_delta(2.0, 1.8) + 0.2) < 1e-9
    assert abs(raw_odds_delta(1.8, 2.0) - 0.2) < 1e-9


def test_implied_prob_delta():
    delta = implied_prob_delta(2.0, 1.8)
    assert delta is not None
    assert delta > 0


def test_beat_later_price_logic():
    assert beat_later_price(None, 1.8) is None
    assert beat_later_price(2.0, 1.8) is True
    assert beat_later_price(1.8, 2.0) is False


def test_summarize_clv_empty():
    summary = summarize_clv([])
    assert summary["total_picks"] == 0
    assert summary["with_two_prices"] == 0
    assert summary["avg_raw_odds_delta"] is None
    assert summary["avg_implied_prob_delta"] is None
    assert summary["beat_later_price_rate"] is None


def test_summarize_clv_tiny_sample():
    rows = [
        {"first_odds": 2.0, "last_odds": 1.8},
        {"first_odds": 1.8, "last_odds": 1.9},
        {"first_odds": None, "last_odds": 1.7},
    ]
    summary = summarize_clv(rows)
    assert summary["total_picks"] == 3
    assert summary["with_two_prices"] == 2
    assert summary["avg_raw_odds_delta"] == -0.05
    assert summary["beat_later_price_n"] == 2
    assert summary["beat_later_price_rate"] == 0.5
