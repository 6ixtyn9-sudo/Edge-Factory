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
