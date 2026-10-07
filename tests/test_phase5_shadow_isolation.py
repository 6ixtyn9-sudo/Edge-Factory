from __future__ import annotations

import ast
import csv
import gzip
import importlib.util
import json
import sys
import types
from argparse import Namespace
from pathlib import Path

import pytest

from edgefactory import phase5_shadow as shadow
from edgefactory import warehouse

ROOT = Path(__file__).resolve().parent.parent


def _load_script(module_name: str, relpath: str):
    script = ROOT / relpath
    spec = importlib.util.spec_from_file_location(module_name, script)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _put_shadow_rows(root: Path) -> None:
    fixture = {
        "date": "2099-01-01",
        "home": "Alpha FC",
        "away": "Beta FC",
        "p1": 0.82,
        "px": 0.10,
        "p2": 0.08,
        "kickoff": "2099-01-01T20:00:00Z",
        "league": "Test League",
    }
    for source in ("vitibet", "betclan"):
        shadow.append_shadow_rows(
            source, [fixture], capture_day="2098-12-31", root=root
        )


def test_warehouse_mining_input_ignores_phase5_directory_even_if_mutated(tmp_path, monkeypatch):
    """Even a source-shaped CSV inside the sidecar cannot enter source views."""
    monkeypatch.setattr(warehouse, "LOCALDATA", tmp_path)
    header = [
        "date", "home", "away", "hs", "gs", "p1", "px", "p2", "league",
        "tip", "pred_hs", "pred_gs", "status", "kickoff",
    ]

    def write_csv(path: Path, home: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "wt", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=header)
            writer.writeheader()
            writer.writerow({
                "date": "2099-01-01", "home": home, "away": "Away FC",
                "hs": "", "gs": "", "p1": "82", "px": "10", "p2": "8",
                "league": "Test League", "tip": "1", "pred_hs": "", "pred_gs": "",
                "status": "", "kickoff": "2099-01-01T20:00:00Z",
            })

    # One legitimate production input plus a hostile nested file that would
    # contaminate the view if its existing top-level glob became recursive.
    write_csv(tmp_path / "vitibet_2099-01.csv.gz", "Production FC")
    write_csv(tmp_path / shadow.SHADOW_DIR / "vitibet_shadow.csv.gz", "Shadow FC")
    _put_shadow_rows(tmp_path)

    connection = warehouse.connect()
    try:
        homes = [row[0] for row in connection.execute("SELECT home FROM vitibet").fetchall()]
    finally:
        connection.close()

    assert homes == ["Production FC"]


def test_shadow_ledger_cannot_vote_or_emit_picks(tmp_path, monkeypatch):
    picks = _load_script("phase5_isolation_picks_today", "scripts/picks_today.py")
    _put_shadow_rows(tmp_path)

    # Network adapters are mocked offline; every normal adapter has an empty
    # response. A control with the same two source rows WOULD vote and emit.
    for name in picks.ALL_SOURCES:
        module = types.ModuleType(f"edgefactory.sources.{name}")
        module.fetch_day = lambda day: []
        monkeypatch.setitem(sys.modules, f"edgefactory.sources.{name}", module)

    monkeypatch.setattr(picks, "load_ml_rules_and_model", lambda: ([], None))
    monkeypatch.setattr(picks, "load_ml_fade_rules", lambda: [])
    day = "2099-01-01"
    thresholds = {
        2: {
            "n_way": 2,
            "threshold": 60.0,
            "rule": "2way avg_p>=60",
            "display_rule": "2WAY>=60",
        }
    }

    unmodified_data = picks.fetch_all(day)
    emitted, vetoes, upcoming, _ = picks.run_day(
        day, thresholds, None, None, source_weights_1x2={}
    )
    assert all(not rows for rows in unmodified_data.values())
    assert emitted == []
    assert vetoes == 0
    assert upcoming == 0

    # Mutation-test control: if the two shadow rows are admitted to the source
    # vote maps, the existing production evaluator can emit a pick. This makes
    # the no-emission assertion above a live guard, not a vacuous empty case.
    key = (picks.source_team_key("Alpha FC"), picks.source_team_key("Beta FC"))
    control_row = {
        "date": day, "home": "Alpha FC", "away": "Beta FC",
        "p1": 0.82, "px": 0.10, "p2": 0.08,
        "kickoff": "2099-01-01T20:00:00Z", "league": "Test League",
    }
    control_data = {
        "vitibet": {key: dict(control_row)},
        "betclan": {key: dict(control_row)},
    }
    monkeypatch.setattr(picks, "fetch_all", lambda requested_day: control_data)
    control_emitted, _vetoes, _upcoming, _ = picks.run_day(
        day, thresholds, None, None, source_weights_1x2={}
    )
    assert len(control_emitted) == 1
    assert control_emitted[0]["sources_used"] == ["vitibet", "betclan"]


def test_phase5_rows_cannot_create_acca_or_change_bank(tmp_path, monkeypatch):
    tickets = _load_script("phase5_isolation_auto_tickets", "scripts/auto_tickets.py")
    target = "2099-01-01"
    monkeypatch.setattr(tickets, "LOCALDATA", tmp_path)
    monkeypatch.setattr(tickets, "STATE_FILE", tmp_path / "auto_tickets_state.json")
    (tmp_path / "picks_today.json").write_text("[]")

    # Hand-edited worst case: give the shadow ledger two ticket-shaped rows
    # with execution prices. They still must not be consulted by the ticket
    # builder; only picks_today.json is its slate input.
    ledger = tmp_path / shadow.SHADOW_DIR / shadow.ROWS_NAME
    ledger.parent.mkdir(parents=True, exist_ok=True)
    hostile_rows = []
    for home, away in (("Alpha FC", "Beta FC"), ("Gamma FC", "Delta FC")):
        hostile_rows.append({
            "record_type": "phase5_shadow_prediction",
            "source": "betminer",
            "date": target,
            "home": home,
            "away": away,
            "market": "1x2",
            "pick": "home",
            "avg_p": 85.0,
            "odds": 2.0,
            "odds_source": "bzzoiro_odds",
            "price_evidence": "NAMED_BOOK_CAPTURE",
            "price_push_eligible": True,
            "price_corroboration_sufficient": True,
            "bucket": "CERTIFIED_CLEAN",
            "kickoff": "2099-01-01T20:00:00Z",
            "kickoff_utc": "2099-01-01T20:00:00+00:00",
        })
    ledger.write_text("\n".join(json.dumps(row) for row in hostile_rows) + "\n")

    monkeypatch.setattr(tickets, "load_settled", lambda: [])
    monkeypatch.setattr(tickets, "is_frozen", lambda *_args, **_kwargs: False)
    monkeypatch.setattr(tickets, "load_archived_picks", lambda: [])
    monkeypatch.setattr(tickets, "compute_bucket_pnl", lambda *_args, **_kwargs: ({}, {}))
    monkeypatch.setattr(tickets, "ensure_slice_seeded", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(tickets, "compute_bucket_slice", lambda *_args, **_kwargs: ({}, {}))
    monkeypatch.setattr(tickets, "upsert_slice_day", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(tickets, "format_skip_census", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(tickets, "_slice_table_lines", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(tickets, "build_rejection_ledger", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(tickets, "_shadow_record_scored", lambda *_args, **_kwargs: {})
    monkeypatch.setattr(tickets, "_shadow_record_outcome", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(tickets, "price_supply_report", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(tickets, "_superseded_no_bet_lines", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(tickets, "live_kickoff_guard", lambda pool, _now: (pool, {}))

    original_plan_day = tickets.plan_day
    plan_calls: list[int] = []

    def track_plan(pool, bank_pct, **kwargs):
        plan_calls.append(len(pool))
        return original_plan_day(pool, bank_pct, **kwargs)

    monkeypatch.setattr(tickets, "plan_day", track_plan)
    state = tickets.fresh_state()
    original_bank = state["bank"]
    result = tickets.cmd_today(Namespace(date=target, force=True), state)

    assert result == 0
    assert plan_calls == []
    assert tickets.effective_bank(state) == original_bank
    assert state["bank"] == original_bank
    assert state["open_slips"] == []
    assert not (tmp_path / f"auto_tickets_{target}.txt").exists()


def test_production_consumers_have_no_phase5_reader_imports():
    consumers = [
        ROOT / "src" / "edgefactory" / "warehouse.py",
        ROOT / "scripts" / "mine_consensus.py",
        ROOT / "scripts" / "picks_today.py",
        ROOT / "scripts" / "auto_tickets.py",
    ]
    for path in consumers:
        tree = ast.parse(path.read_text())
        phase5_imports = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module == "edgefactory.phase5_shadow"
        ]
        if path.name == "picks_today.py":
            assert len(phase5_imports) == 1
            imported = {alias.name for alias in phase5_imports[0].names}
            assert imported == {
                "append_capture_attempt", "append_shadow_rows", "local_capture_date"
            }
        else:
            assert phase5_imports == []

    # The sidecar boundary is a writer-only dependency; no production voter,
    # emitter, ticket, or bank module has a reader API to call.
    assert not any(
        callable(value) and (name.startswith("read_") or name.startswith("load_"))
        for name, value in vars(shadow).items()
        if not name.startswith("_")
    )
