from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
SCRIPT = ROOT / "scripts" / "remine_backfill.py"
spec = importlib.util.spec_from_file_location("remine_backfill_under_test", SCRIPT)
assert spec and spec.loader
remine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(remine)


def _configure(tmp_path: Path, monkeypatch, inventory: dict) -> None:
    localdata = tmp_path / "localdata"
    localdata.mkdir()
    inventory_path = localdata / "coverage_inventory.json"
    inventory_path.write_text(json.dumps(inventory), encoding="utf-8")
    monkeypatch.setattr(remine, "ROOT", tmp_path)
    monkeypatch.setattr(remine, "LOCALDATA", localdata)
    monkeypatch.setattr(remine, "INVENTORY_PATH", inventory_path)
    monkeypatch.setattr(remine, "LEDGER_PATH", localdata / "backfill_ledger.jsonl")
    monkeypatch.setattr(remine, "RAW_ROOT", localdata / "remine_raw")
    monkeypatch.setenv("EDGE_FACTORY_RUN_DATE", "2026-10-02")


def _inventory(days: list[str]) -> dict:
    return {
        "sources": {
            "statarea": {"date_range": {"no_matches_days": ["2020-04-14", "2020-04-28", "2020-12-25"]}},
        },
        "crawl_plan_inputs": {
            "betexplorer_results": {"proposed_internal_gap_days": days},
        },
    }


def test_dry_run_holds_audited_statarea_without_writes(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch, _inventory(["2026-06-17"]))
    audit = remine.LOCALDATA / "remine_audit_2026-10-02.jsonl"
    audit.write_text(
        "\n".join(
            json.dumps({"source": "statarea", "date": day, "status": "no_matches_day", "checksum_status": "relay_no_raw_bytes"})
            for day in ("2020-04-14", "2020-04-28", "2020-12-25")
        )
        + "\n",
        encoding="utf-8",
    )

    result = remine.run(dry_run=True)

    assert result["statarea_held"] == 3
    assert result["betexplorer"]["requests"] == 0
    assert result["football_data"]["status"] == "gated"
    assert not remine.LEDGER_PATH.exists(), "dry-run must not create runner state"


def test_betexplorer_consumes_at_most_ten_dates_and_writes_raw_receipts(tmp_path, monkeypatch):
    days = [f"2026-06-{day:02d}" for day in range(17, 29)]
    _configure(tmp_path, monkeypatch, _inventory(days))

    from edgefactory.sources import betexplorer_odds

    calls: list[str] = []
    monkeypatch.setattr(betexplorer_odds, "reset_fetch_count", lambda: None)
    monkeypatch.setattr(betexplorer_odds, "last_response_bytes", lambda: b"runner response")

    def fetch(day: str):
        calls.append(day)
        betexplorer_odds.LAST_RESULTS_RECEIPT = {
            "status": "success", "date": day, "url": f"https://example/{day}",
            "response_bytes": 15, "sha256": "transport-sha",
        }
        return [{"date": day, "kickoff": "12:00", "home": "Alpha", "away": "Beta", "event_id": day}]

    monkeypatch.setattr(betexplorer_odds, "fetch_day_matches", fetch)
    result = remine.run()

    assert calls == days[:10]
    assert result["betexplorer"]["requests"] == 10
    assert result["betexplorer"]["remaining"] == 2
    ledger = remine._read_jsonl(remine.LEDGER_PATH)
    receipts = [row for row in ledger if row.get("source") == "betexplorer_results" and row.get("status") == "success"]
    assert len(receipts) == 10
    assert all(row["raw_artifact"] for row in receipts)
    assert all(row["existing_wins_collisions"] == 0 for row in receipts)


def test_betexplorer_challenge_freezes_source_without_marking_day_empty(tmp_path, monkeypatch):
    _configure(tmp_path, monkeypatch, _inventory(["2026-06-17", "2026-06-18"]))
    from edgefactory.sources import betexplorer_odds

    monkeypatch.setattr(betexplorer_odds, "reset_fetch_count", lambda: None)
    monkeypatch.setattr(betexplorer_odds, "fetch_day_matches", lambda _day: (_ for _ in ()).throw(betexplorer_odds.BetExplorerChallenge("challenge")))
    result = remine.run()

    assert result["betexplorer"]["frozen"] is True
    assert result["betexplorer"]["requests"] == 1
    statuses = [row["status"] for row in remine._read_jsonl(remine.LEDGER_PATH)]
    assert "source_freeze" in statuses
    assert "no_matches_day" not in statuses
