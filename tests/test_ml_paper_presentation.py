"""TXT-only spacing changes must not touch forward receipts or lane decisions."""

from copy import deepcopy

import pytest
from test_ml_paper import DAY, candidate, capture, receipt

from edgefactory import ml_paper as mp


def card():
    first = candidate(1, odds=2.12, p=0.696, bucket="SKIPPED_VETO")
    first.update(home="Radomiak Radom", away="Śląsk Wrocław")
    second = candidate(2, odds=1.35, p=0.808, market="match_over_25")
    second.update(home="Benfica", away="Alverca", selection="over")
    row = receipt(DAY, [first, second], [
        {"odds": 2.862, "stake_units": 8.196803, "book": "Betsson",
         "legs": [first, second]},
    ])
    row.update(
        frozen_at="2026-11-02T07:16:00.824102+00:00",
        coverage={"candidate_count": 109, "candidate_fixtures": 2,
                  "slate_rows": 7, "status": "inputs_available"},
        rejections={"data_quality": 1, "quote_or_probability_unavailable": 69},
    )
    return row


def test_ticket_txt_has_separate_leg_diagnostics_and_freeze_blocks():
    row = card()
    before = deepcopy(row)
    text = mp.render_card(row)
    assert text == (
        "autobets_ML TICKETS — 2026-11-02\n" + "=" * 62 + "\n\n"
        "PAPER ONLY — own legs, accas and model-sized stakes; no odds band.\n"
        "Same-book single-price products; acca acceptance/payout unconfirmed.\n\n"
        "[PAPER ACCA #1] @2.862 — 8.196803 paper units — Betsson\n"
        "   Radomiak Radom vs Śląsk Wrocław\n"
        "      1x2 home @2.120 · ML 69.6% · SKIPPED_VETO\n"
        "      Source forecast unavailable · quote age unavailable\n\n"
        "   Benfica vs Alverca\n"
        "      match_over_25 over @1.350 · ML 80.8% · CAUTION\n"
        "      Source forecast unavailable · quote age unavailable\n\n"
        "LEGACY STAKING — no fixture-cap policy is declared on this frozen receipt.\n"
        "   Historical stakes are preserved; the new gross fixture budget applies to new publications.\n\n"
        "COVERAGE\n"
        "   Candidate count: 109\n"
        "   Candidate fixtures: 2\n"
        "   Slate rows: 7\n"
        "   Status: inputs_available\n\n"
        "REJECTIONS\n"
        "   Data quality: 1\n"
        "   Quote or probability unavailable: 69\n\n"
        "ADMISSION  CAUTION / SKIPPED_VETO are intentionally paper-eligible; data-quality guards remain.\n\n"
        "LEARNING  awaiting_prior_paper_results\n\n"
        "FREEZE   2026-11-02T07:16:00.824102+00:00 | paper_accas\n"
    )
    assert row == before


def test_multiple_accas_have_blank_line_between_blocks():
    row = card()
    row["accas"].append(deepcopy(row["accas"][0]))
    text = mp.render_card(row)
    assert "quote age unavailable\n\n[PAPER ACCA #2]" in text
    assert text.count("[PAPER ACCA #") == 2


@pytest.mark.parametrize("status, message", [
    ("no_paper_bet", "no qualifying model/price/capital combination."),
    ("missed_freeze_no_paper_bet", "missed 09:00 freeze; no late backfill."),
])
def test_no_bet_card_keeps_reason_and_spacing(status, message):
    row = card()
    row.update(status=status, accas=[])
    text = mp.render_card(row)
    assert f"\n\nNO PAPER BET — {message}\n\nCOVERAGE\n" in text
    assert "[PAPER ACCA" not in text
    assert text.endswith(f" | {status}\n")


def test_legacy_card_without_diagnostics_or_actual_freeze_is_readable():
    row = receipt(DAY, [])
    text = mp.render_card(row)
    assert "COVERAGE\n   None recorded\n\nREJECTIONS\n   None recorded\n" in text
    assert f"FREEZE   {row['freeze_at']} | no_paper_bet\n" in text


def test_draft_card_retains_status_and_scheduled_time():
    row = card()
    row.pop("frozen_at")
    row["status"] = "draft_not_yet_frozen"
    assert mp.render_card(row).endswith(
        f"FREEZE   {row['freeze_at']} | draft_not_yet_frozen\n"
    )


def test_performance_spacing_preserves_bank_and_risk_caveats():
    report = mp.performance([], lambda leg: None)
    before = deepcopy(report)
    text = mp.render_performance(report)
    assert "=" * 62 + "\n\nBANK" in text
    assert "reserved paper units\n\nRECORD" in text
    assert "missed freeze\n\nEVIDENCE" in text
    assert "\n\nSTAKING" in text
    assert "ROI not measured yet" in text
    assert "not a confirmed acca quote\n\nPaper only." in text
    assert report == before


def test_publish_refreshes_readable_txt_without_changing_frozen_evidence(tmp_path):
    row = capture(tmp_path)
    receipt_path = mp.receipt_path(tmp_path, DAY)
    state_path = mp.state_path(tmp_path)
    before = {p: p.read_bytes() for p in (receipt_path, state_path)}
    (tmp_path / f"{mp.PREFIX}_{DAY}.txt").write_text("old compact display\n")
    mp.publish(tmp_path, lambda leg: None)
    assert (tmp_path / f"{mp.PREFIX}_{DAY}.txt").read_text() == mp.render_card(row)
    assert all(p.read_bytes() == data for p, data in before.items())
