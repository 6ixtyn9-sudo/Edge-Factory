from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "audit_clv.py"
SPEC = importlib.util.spec_from_file_location("audit_clv", SCRIPT)
audit_clv = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(audit_clv)


def test_single_snapshot_is_not_counted_as_two_prices():
    rows = [
        {
            "pick_id": "a",
            "rule_name": "rule1",
            "bucket": "CAUTION",
            "observed_odds": "1.80",
            "snapshot_label": "pick_time",
            "captured_at_utc": "2026-06-17T10:00:00Z",
        }
    ]
    comparisons, meta = audit_clv._comparison_rows(rows)
    assert len(comparisons) == 1
    assert comparisons[0]["first_odds"] == 1.8
    assert comparisons[0]["last_odds"] is None
    assert meta["insufficient_snapshots"] == 1

    summary = audit_clv.summarize_clv(comparisons)
    assert summary["total_picks"] == 1
    assert summary["with_two_prices"] == 0
    assert summary["avg_raw_odds_delta"] is None
    assert summary["beat_later_price_rate"] is None


def test_two_snapshots_are_compared_normally():
    rows = [
        {
            "pick_id": "a",
            "rule_name": "rule1",
            "bucket": "CAUTION",
            "observed_odds": "2.00",
            "snapshot_label": "pick_time",
            "captured_at_utc": "2026-06-17T10:00:00Z",
        },
        {
            "pick_id": "a",
            "rule_name": "rule1",
            "bucket": "CAUTION",
            "observed_odds": "1.90",
            "snapshot_label": "latest",
            "captured_at_utc": "2026-06-17T12:00:00Z",
        },
    ]
    comparisons, meta = audit_clv._comparison_rows(rows)
    assert meta["insufficient_snapshots"] == 0
    assert comparisons[0]["first_odds"] == 2.0
    assert comparisons[0]["last_odds"] == 1.9

    summary = audit_clv.summarize_clv(comparisons)
    assert summary["with_two_prices"] == 1
    assert summary["avg_raw_odds_delta"] == -0.1
    assert summary["beat_later_price_rate"] == 1.0


# ===========================================================================
# CLV records the verdict for THIS selection, not merely for its date
# ===========================================================================


FROZEN_OUTCOME = {"2026-10-01": {
    "status": "ticket_frozen",
    "frozen_leg_keys": ["bnei yehuda|maccabi kiryat gat|home",
                        "envigado|orsomarso|home"]}}


def _sel(home, away, pick="home"):
    return {"event_date": "2026-10-01", "home": home, "away": away,
            "pick": pick}


def test_a_selection_on_the_frozen_card_is_frozen():
    assert audit_clv._selection_ticket_status(
        _sel("Envigado", "Orsomarso"), FROZEN_OUTCOME) == "ticket_frozen"


def test_a_selection_added_after_the_freeze_is_not_ticketed():
    """Run 84619f7: Maccabi Bnei Raina was never on the frozen card."""
    assert audit_clv._selection_ticket_status(
        _sel("Maccabi Bnei Raina", "Hapoel Kfar Shalem"),
        FROZEN_OUTCOME) == audit_clv.DECLINED_FROZEN_CARD


def test_an_outcome_without_leg_records_keeps_the_date_status():
    assert audit_clv._selection_ticket_status(
        _sel("Anything", "At All"),
        {"2026-10-01": {"status": "ticket_frozen"}}) == "ticket_frozen"


def test_a_declined_date_is_passed_through_unchanged():
    assert audit_clv._selection_ticket_status(
        _sel("Anything", "At All"),
        {"2026-10-01": {"status": "declined_insufficient_legs"}}
    ) == "declined_insufficient_legs"


def test_an_unknown_date_is_pending_not_invented():
    assert audit_clv._selection_ticket_status(
        _sel("Anything", "At All"), {}) == audit_clv.PENDING_TICKET_STATUS
