"""Financial presentation parity without recalculating or resetting paper state."""

import json
import math
from copy import deepcopy

import pytest
from test_ml_paper import DAY, candidate, receipt

from edgefactory import ml_paper as mp


def acca(legs, *, stake=2):
    return {"legs": legs, "stake_units": stake, "odds": math.prod(c["odds"] for c in legs), "book": "Pinnacle"}


def history():
    cs = [candidate(i, odds=1.5 if i % 2 else 2) for i in range(1, 9)]
    first = receipt(DAY, cs[:4], [acca(cs[:2]), acca(cs[2:4], stake=3)])
    second = receipt(DAY, cs[4:6], [acca(cs[4:6], stake=1)])
    second.update(decision_id="second-publication", freeze_basis=mp.ROLLING_FREEZE,
                  frozen_at=second["persisted_at"])
    next_day = "2026-11-03"
    later_cs = [candidate(i, date=next_day, odds=1.5 if i % 2 else 2) for i in (7, 8)]
    last = receipt(next_day, later_cs, [acca(later_cs, stake=4)])
    return [first, second, last]


def results(leg):
    # First acca wins (+4), second loses (-3), other two are pending.
    return (2, 0) if leg["candidate_id"] in {"1", "2"} else ((0, 1) if leg["candidate_id"] == "3" else None)


def test_financial_summary_and_grouped_bet_days_match_existing_report():
    rows = history()
    report = mp.performance(rows, results)
    before = deepcopy((rows, report))
    text = mp.render_performance(report)
    assert "BANK     101.0%   x1.010" in text
    assert "CAPITAL  96.0% free / 5.0% reserved" in text
    assert "RECORD   1W / 1L   (50.0% hit)   over 2 bet-days" in text
    assert "OPEN     2 held accas" in text
    assert "PROFIT   +1.0% of capital · +1.000 paper units · ROI +20.0%" in text
    table = text.split("BET-DAYS, oldest first", 1)[1].split("HELD (not yet settled", 1)[0]
    assert "(2 of 2)" in table and table.count(DAY) == 1
    assert "2026-11-02   1W/1L   staked    5.0%   returned    6.0%   net   +1.0%   pending    1.0%   bank*  101.0%" in table
    assert "2026-11-03   0W/0L   staked    0.0%   returned       —   net       —   pending    4.0%   bank*  101.0%" in table
    assert table.index(DAY) < table.index("2026-11-03")
    assert "reconstructed from latest known results by ticket date" in text
    assert "not stored historical daily closes" in text
    assert (rows, report) == before


def test_held_numbers_count_settled_tickets_and_match_daily_labels():
    report = mp.performance(history(), results)
    held = mp.render_performance(report).split("HELD (not yet settled; stake counted as committed)")[1].split("NOTES")[0]
    assert f"{DAY}   ACCA #3 @3.000" in held
    assert "2026-11-03   ACCA #1 @3.000" in held
    assert "Receipt second-publication / publication-local ticket 1" in held
    assert held.count("HELD (not settled)") == report["pending_accas"] == 2
    assert "Home Club 5 vs Away Club 5" in held and "Home Win (1X2) @1.500" in held
    assert "14:00 SAST" in held
    assert "Home Club 3 vs Away Club 3" not in held  # loss already settled despite missing fourth leg


def test_known_loss_is_never_held_just_because_another_leg_is_unresolved():
    cs = [candidate(1), candidate(2)]
    row = receipt(DAY, cs, [acca(cs)])
    report = mp.performance([row], lambda leg: (0, 1) if leg["candidate_id"] == "1" else None)
    text = mp.render_performance(report)
    assert "RECORD   0W / 1L" in text and "OPEN     0 held accas" in text
    assert "PROFIT   -2.0% of capital" in text
    assert "HELD (not yet settled; stake counted as committed)\n  None." in text
    assert report["unresolved_result_legs"] == 1
    assert "known losing leg settles its acca as a loss" in text


def test_no_history_has_no_invented_bet_days_results_or_cycle_policy():
    report = mp.performance([], lambda leg: None)
    text = mp.render_performance(report)
    assert "BANK     100.0%" in text and "hit rate not measured yet" in text
    assert "ROI not measured yet" in text
    assert "BET-DAYS, oldest first (0 of 0)" in text and "No bet days recorded." in text
    assert "HELD (not yet settled; stake counted as committed)\n  None." in text
    assert "CYCLE" not in text and "take-profit" not in text
    assert "Main" not in text and "ENH" not in text


def test_empty_publications_do_not_create_flat_bet_day_rows_or_reset_losses():
    rows = history()
    rows.insert(1, receipt(DAY, []))
    rows.append(receipt("2026-11-04", []))
    report = mp.performance(rows, results)
    text = mp.render_performance(report)
    table = text.split("BET-DAYS, oldest first", 1)[1].split("HELD (not yet settled", 1)[0]
    assert "(2 of 2)" in table and "2026-11-04" not in table
    assert "DAYS     2 bet / 1 no-bet" in text
    assert "BANK     101.0%" in text
    assert "All retained history is included; no regime reset or old-loss exclusion." in text


def test_percentages_use_initial_base_not_current_free_bank():
    report = mp.performance(history(), results)
    scaled = deepcopy(report)
    for field in ("base_paper_units", "paper_bank_units", "paper_free_units", "paper_committed_units",
                  "profit_units", "settled_stake_units", "max_daily_close_drawdown_units"):
        scaled[field] *= 2
    for row in scaled["history"]:
        for item in row["accas"]:
            item["stake_units"] *= 2
            if item["profit_units"] is not None:
                item["profit_units"] *= 2
    text = mp.render_performance(scaled)
    assert "BANK     101.0%" in text and "· 202.000 paper units" in text
    assert "initial 200-paper-unit base" in text
    assert "stake 1.0% (2.000000 paper units)" in text
    assert "staked    5.0%   returned    6.0%   net   +1.0%" in text


@pytest.mark.parametrize("base", [0, -100, float("nan"), float("inf")])
def test_invalid_base_fails_instead_of_inventing_percentages(base):
    report = mp.performance([], lambda leg: None)
    report["base_paper_units"] = base
    with pytest.raises(ValueError, match="positive finite base"):
        mp.render_performance(report)


def test_display_is_deterministic_without_mutating_historical_outcomes():
    report = mp.performance(history(), results)
    before = json.dumps(report, sort_keys=True)
    text = mp.render_performance(report)
    assert mp.render_performance(report) == text
    assert json.dumps(report, sort_keys=True) == before
