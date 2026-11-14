"""Enhancement candidate log (logging only; selection is unchanged).

Covers the helper that builds one log row per candidate and the helper that
marks the chosen candidate. Selection itself is covered elsewhere.
"""
import scripts.picks_today as pt


def test_entry_records_exclusion_and_price_fields():
    e = pt._enh_log_entry(
        "match_over_15", "Match Over 1.5 Goals", "excluded", "below_min_leg_odds",
        probability=0.8123456, raw_probability=0.79, cohort_rate=0.75,
        engine="hybrid_cohort", price=1.25, price_source="scoutingstats",
        price_book="Betsson",
    )
    assert e["market"] == "match_over_15"
    assert e["status"] == "excluded"
    assert e["reason"] == "below_min_leg_odds"
    assert e["probability"] == 0.8123
    assert e["raw_probability"] == 0.79
    assert e["cohort_rate"] == 0.75
    assert e["engine"] == "hybrid_cohort"
    assert e["price"] == 1.25
    assert e["price_source"] == "scoutingstats"
    assert e["price_book"] == "Betsson"
    # Raw 1/price, not de-vigged.
    assert e["implied_probability"] == round(1 / 1.25, 4)


def test_entry_without_price_has_no_implied_probability():
    e = pt._enh_log_entry("btts_yes", "BTTS Yes", "excluded", "unpriced", probability=0.6)
    assert e["price"] is None
    assert e["implied_probability"] is None
    assert e["reason"] == "unpriced"


def test_mark_selected_picks_first_matching_eligible_only():
    log = [
        pt._enh_log_entry("match_over_25", "O2.5", "eligible", None, price=1.4),
        pt._enh_log_entry("match_over_15", "O1.5", "eligible", None, price=1.3),
        pt._enh_log_entry("btts_yes", "BTTS", "excluded", "unpriced"),
    ]
    pt._enh_log_mark_selected(log, "match_over_15")
    statuses = {e["market"]: e["status"] for e in log}
    assert statuses == {
        "match_over_25": "eligible_not_selected",
        "match_over_15": "recommended",
        "btts_yes": "excluded",
    }


def test_mark_selected_with_no_choice_leaves_eligible_as_not_selected():
    log = [pt._enh_log_entry("match_over_25", "O2.5", "eligible", None, price=1.4)]
    pt._enh_log_mark_selected(log, None)
    assert log[0]["status"] == "eligible_not_selected"
