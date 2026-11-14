"""Daily rolling display changes labels, never decisions or frozen evidence."""

import json
import re
from copy import deepcopy
from datetime import timedelta

import pytest
from test_ml_paper import DAY, NOW, candidate, receipt
from test_ml_paper_rolling import run, slate

from edgefactory import ml_paper as mp


def publication(offset=0, *, count=1):
    legs = [candidate(offset * 2 + i) for i in (1, 2)]
    row = receipt(DAY, legs, [
        {"odds": 4.0, "stake_units": 1.234567, "book": "Betsson", "legs": legs}
        for _ in range(count)
    ])
    captured = NOW + timedelta(minutes=offset)
    row.update(
        captured_at=captured.isoformat(), frozen_at=(captured + timedelta(seconds=1)).isoformat(),
        decision_id=captured.strftime("%Y%m%dT%H%M%S%fZ"), freeze_basis=mp.ROLLING_FREEZE,
        paper_bank_at_decision=100, window_start=captured.isoformat(),
        window_end=(captured + timedelta(hours=24)).isoformat(),
        coverage={"candidate_count": 2}, rejections={"data_quality": offset},
    )
    return row


def numbers(text):
    return [int(n) for n in re.findall(r"^\[PAPER ACCA #(\d+)\]", text, re.MULTILINE)]


def test_one_header_and_daily_numbers_with_exact_frozen_local_index_mapping():
    first, empty, last = publication(count=2), publication(1, count=0), publication(2)
    rows = [last, first, empty]  # renderer must not rely on caller order or mutate it
    before = deepcopy(rows)
    text = mp.render_daily_card(rows, audit=True)
    assert text.count("autobets_ML TICKETS") == 1
    assert numbers(text) == [1, 2, 3]
    assert "reference P1/1" in text and "reference P1/2" in text and "reference P3/1" in text
    assert "P2 · 2026-11-02 08:01:01 SAST · No additional tickets" in text
    assert "NO PAPER BET" not in text
    assert all(r["decision_id"] in text and r["frozen_at"] in text for r in rows)
    assert text.count("ADMISSION ") == 1
    assert text.count("acca acceptance/payout unconfirmed") == 1
    assert text.count("1.234567 paper units — Betsson") == 3
    assert rows == before


def test_leg_forecast_and_quote_details_are_below_tickets_not_dropped():
    row = publication()
    row["accas"][0]["legs"][0].update(
        ml_inputs={"values": {"forecast_1x2_home_mean": 0.6}},
        price_at=(NOW - timedelta(minutes=30)).isoformat(),
    )
    text = mp.render_daily_card([row], audit=True)
    tickets, details = text.split("PUBLICATION & LEG DETAILS", 1)
    assert tickets.count("KICKOFF 2026-11-02 14:00 SAST") == 2
    assert "Home Win (1X2) @2.000 · ML 70.0% · CAUTION" in tickets
    assert "quote age" not in tickets and "source forecast" not in tickets
    assert "ACCA #1 / leg 1: source forecast 60.0% · gap +10.0 pp · quote age 0.50h at decision" in details
    assert "quote age unavailable" in details
    assert "Coverage: candidate count: 2" in details and "Rejections: data quality: 0" in details


def test_initial_empty_scan_is_not_a_day_level_no_bet_after_later_tickets():
    text = mp.render_daily_card([publication(count=0), publication(1)], audit=True)
    assert "NO PAPER BET" not in text
    assert "No tickets at this publication" in text
    assert numbers(text) == [1] and "reference P2/1" in text


def test_all_empty_publications_have_one_no_bet_notice_and_no_acca_numbers():
    rows = [publication(count=0), publication(1, count=0)]
    text = mp.render_daily_card(rows, audit=True)
    assert text.count("NO PAPER BET") == 1 and numbers(text) == []
    assert all(r["decision_id"] in text for r in rows)


def test_append_only_publications_keep_display_numbers_and_original_identity():
    first = publication(count=2)
    initial = mp.render_daily_card([first], audit=True)
    later = mp.render_daily_card([first, publication(1, count=0), publication(2)], audit=True)
    initial_tickets = initial.split("PUBLICATION & LEG DETAILS")[0]
    later_tickets = later.split("[PAPER ACCA #3]")[0]
    # Header counters differ; the two existing ticket blocks must not.
    assert initial_tickets[initial_tickets.index("[PAPER ACCA #1]"):] == later_tickets[later_tickets.index("[PAPER ACCA #1]"):]


def test_current_bank_is_explicitly_not_an_old_decision_balance():
    report = {"paper_bank_units": 91.803197, "paper_free_units": 80, "paper_committed_units": 11.803197}
    row = publication()
    before = deepcopy((row, report))
    text = mp.render_daily_card([row], report, audit=True)
    assert "CURRENT PAPER BANK (all dates): 91.803 units · free 80.000 / reserved 11.803" in text
    assert "Bank at decision: 100.000000 paper units" in text
    assert (row, report) == before


@pytest.mark.parametrize("market,selection,label", [
    ("1x2", "home", "Home Win (1X2)"), ("1x2", "away", "Away Win (1X2)"),
    ("1x2", "draw", "Draw (1X2)"),
    ("double_chance", "1x", "Double Chance — Home or Draw (1X)"),
    ("double_chance", "away", "Double Chance — Draw or Away (X2)"),
    ("double_chance", "12", "Double Chance — No Draw (12)"),
    ("btts_yes", "yes", "Both Teams To Score — Yes"),
    ("btts_no", "no", "Both Teams To Score — No"),
    ("match_over_25", "over", "Match Over 2.5 Goals"),
    ("match_under_45", "under", "Match Under 4.5 Goals"),
    ("home_over_05", "over", "Home Team Over 0.5 Goals"),
    ("away_under_15", "under", "Away Team Under 1.5 Goals"),
    ("match_over_25", "under", "match_over_25 under"),
    ("btts_no", "yes", "btts_no yes"), ("unknown_market", "away", "unknown_market away"),
])
def test_market_labels_preserve_side_and_line_without_guessing(market, selection, label):
    leg = {"market": market, "selection": selection}
    before = dict(leg)
    assert mp._paper_market_label(leg) == label
    assert leg == before


@pytest.mark.parametrize("rows", [[], [publication(), dict(publication(1), date="2026-11-03")]])
def test_daily_renderer_rejects_missing_or_mixed_dates(rows):
    with pytest.raises(ValueError, match="exactly one date"):
        mp.render_daily_card(rows)


def test_mixed_legacy_and_rolling_receipts_keep_original_freeze_basis():
    legacy = publication()
    legacy.pop("freeze_basis")
    text = mp.render_daily_card([legacy, publication(1)], audit=True)
    assert "basis legacy daily freeze" in text
    assert f"basis {mp.ROLLING_FREEZE}" in text
    assert numbers(text) == [1, 2]
    assert text.count("LEGACY STAKING") == 2


def test_publish_changes_only_txt_view_not_receipts_stakes_or_state(tmp_path, monkeypatch):
    first = run(tmp_path)
    empty = run(tmp_path, NOW + timedelta(minutes=1), slate(NOW + timedelta(minutes=1), ids=(3,)))
    later = run(tmp_path, NOW + timedelta(minutes=2), slate(NOW + timedelta(minutes=2), ids=(4, 5)))
    assert first["accas"] and not empty["accas"] and later["accas"]
    history = mp.receipts(tmp_path)
    originals = {p: p.read_bytes() for p in mp.receipt_files(tmp_path)}
    if mp.state_path(tmp_path).exists():
        originals[mp.state_path(tmp_path)] = mp.state_path(tmp_path).read_bytes()
    history_before = json.dumps(history, sort_keys=True)

    def forbidden(*args, **kwargs):
        raise AssertionError("publishing cannot select, learn or capture")

    for name in ("select_accas", "learn", "candidates", "capture", "capture_rolling"):
        monkeypatch.setattr(mp, name, forbidden)
    report = mp.publish(tmp_path, lambda leg: None)
    text = (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text()
    assert text == mp.render_daily_card(history, report)
    assert numbers(text) == list(range(1, 1 + sum(len(r["accas"]) for r in history)))
    assert "Scans without tickets: 1 scan(s)" in text and "NO PAPER BET" not in text
    audit = (tmp_path / mp.RECEIPT_DIR / "reports" / f"{mp.PREFIX}_{DAY}_audit.txt").read_text()
    assert audit == mp.render_daily_card(history, report, audit=True)
    assert all(r["decision_id"] in audit for r in history)
    assert all(p.read_bytes() == blob for p, blob in originals.items())
    assert json.dumps(mp.receipts(tmp_path), sort_keys=True) == history_before
    assert report == mp.performance(history, lambda leg: None)
    assert not list(tmp_path.glob(f"{mp.PREFIX}_????-??-??*.json"))
