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


# ---------------------------------------------------------------------------
# Task D1 (2026-09-06): owner-recorded actual prices (audit_clv record /
# capture attach / report) — the price the owner actually got, next to the
# engine's quote. Nothing here infers an actual price; an entry is only ever
# what the owner wrote down.
# ---------------------------------------------------------------------------

import csv  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402


def _pick_row(day, home, away, pick, odds, market="1x2", rule="ml-meta-avg-p-55"):
    return {
        "date": day, "home": home, "away": away, "market": market,
        "pick": pick, "odds": odds, "edge_rule": rule,
        "league": "Test League", "kickoff": f"{day}T12:00:00+02:00",
        "avg_p": 0.7, "min_p": 0.6, "edge_status": "certified",
    }


def test_record_writes_and_dedupes_entry(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_clv, "LOCALDATA", tmp_path)
    audit_clv.record("2026-09-07", "Vancouver Whitecaps vs St. Louis City",
                     "HOME", 1.44)
    audit_clv.record("2026-09-07", "Vancouver Whitecaps vs St. Louis City",
                     "HOME", 1.42, recorded_at="2026-09-07T08:00:00+02:00")
    data = json.loads((tmp_path / "actual_odds_2026-09-07.json").read_text())
    assert len(data) == 1
    assert data[0]["actual_odds"] == 1.42
    assert data[0]["recorded_at"] == "2026-09-07T08:00:00+02:00"


def test_record_rejects_non_decimal_odds(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_clv, "LOCALDATA", tmp_path)
    import pytest
    with pytest.raises(SystemExit):
        audit_clv.record("2026-09-07", "A vs B", "HOME", 0.95)


def test_capture_attaches_actual_price_to_matching_snapshot_rows(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_clv, "LOCALDATA", tmp_path)
    day = "2026-09-07"
    picks = [
        _pick_row(day, "Vancouver Whitecaps", "St. Louis City", "HOME", 1.45),
        _pick_row(day, "Vitória", "Casa Pia AC", "HOME", 1.50),
    ]
    inp = tmp_path / "picks_input.json"
    inp.write_text(json.dumps(picks))
    audit_clv.capture(day, "pick_time", inp)

    # owner records the actual offer for one printed leg
    audit_clv.record(day, "Vancouver Whitecaps vs St. Louis City", "HOME", 1.44)

    # second capture run attaches (idempotent merge path)
    audit_clv.capture(day, "pick_time", inp)

    snap_path = tmp_path / f"clv_snapshots_{day[:7]}.csv.gz"
    with gzip.open(snap_path, "rt", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2
    by_match = {r["home"]: r for r in rows}
    vc = by_match["Vancouver Whitecaps"]
    assert vc["actual_odds"] == "1.44"
    assert vc["actual_odds_recorded_at"]  # stamped
    assert vc["observed_odds"] == "1.45"  # engine quote untouched, side by side
    assert by_match["Vitória"]["actual_odds"] in ("", None)


def test_capture_warns_but_keeps_unmatched_entries(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(audit_clv, "LOCALDATA", tmp_path)
    day = "2026-09-07"
    picks = [_pick_row(day, "Vancouver Whitecaps", "St. Louis City", "HOME", 1.45)]
    inp = tmp_path / "picks_input.json"
    inp.write_text(json.dumps(picks))
    audit_clv.record(day, "A Typo Team vs Nobody", "HOME", 1.90)
    audit_clv.capture(day, "pick_time", inp)
    assert "matching no pick: 1" in capsys.readouterr().out


def test_report_includes_actual_price_section(tmp_path, monkeypatch):
    monkeypatch.setattr(audit_clv, "LOCALDATA", tmp_path)
    day = "2026-09-07"
    picks = [_pick_row(day, "Vancouver Whitecaps", "St. Louis City", "HOME", 1.45)]
    inp = tmp_path / "picks_input.json"
    inp.write_text(json.dumps(picks))
    audit_clv.capture(day, "pick_time", inp)
    audit_clv.record(day, "Vancouver Whitecaps vs St. Louis City", "HOME", 1.44)
    audit_clv.capture(day, "end_of_run", inp)  # second label + attach
    audit_clv.report(day, day)
    payload = json.loads((tmp_path / "clv_report_rolling.json").read_text())
    ap = payload["actual_price"]
    assert ap["n_entries"] == 1
    assert ap["n_with_quote"] == 1
    assert ap["mean_delta"] == round(1.44 - 1.45, 6)  # actual shorter than quote
    md = (tmp_path / f"clv_report_{day}.md").read_text()
    assert "Actual price vs engine quote" in md
    assert "mean actual-minus-engine-quote" in md
