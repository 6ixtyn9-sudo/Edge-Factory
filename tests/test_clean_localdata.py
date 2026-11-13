from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import json
from datetime import date
from unittest.mock import patch

import pytest

from scripts.clean_localdata import (
    clean_localdata,
    files_to_prune,
    main,
    morning_archive_is_redundant,
)

TODAY = date(2026, 9, 25)
OLD = "2026-08-01"      # outside a 30-day window ending 2026-09-25
RECENT = "2026-09-01"   # inside it

TELEMETRY = (
    "clv_report_{d}.md",
    "clv_unmatched_{d}.json",
    "sent_ledger_{d}.json",
    "shadow_sent_ledger_{d}.json",
    "discovery_sent_ledger_{d}.json",
    "notify_delivery_failures_{d}.json",
    "theoddsapi_attempts_{d}.json",
    "supabase_sync_manifest_{d}.json",
    "official_run_{d}.json",
    "picks_{d}.txt",
    "picks_audit_{d}.md",
)

# Durable replay/audit data, rolling state, monthly archives and unknown
# files: never pruned, however old.
DURABLE = (
    f"picks_{OLD}.json",
    f"auto_tickets_{OLD}.txt",
    "picks_today.json",
    "picks_next_2days.json",
    "picks_audit_rolling.json",
    "clv_report_rolling.json",
    "auto_tickets_state.json",
    "auto_tickets_slice_ledger.jsonl",
    "settled_results.json",
    "edges_consensus.json",
    "clv_snapshots_2026-06.csv.gz",
    "betexplorer_odds_2026-01.csv.gz",
    "forebet.csv.gz",
    "warehouse.duckdb",
    f"model_{OLD}.bin",                 # unknown dated family
    f"forecast_{OLD}_0900.json",        # not in the known list
    f"ml_fade_research_report_{OLD}.md",
    f"clv_report_{OLD}.md.bak",         # near-miss shape
    f"picks_audit_{OLD}.json",          # near-miss shape
)


def _row(home, away, pick="home", **extra):
    return {"date": extra.pop("date", OLD), "home": home, "away": away,
            "market": "1x2", "pick": pick, "odds": 1.5, **extra}


def _write(path, rows):
    path.write_text(json.dumps(rows))


def test_prunes_old_known_telemetry_and_keeps_everything_else(tmp_path):
    for pattern in TELEMETRY:
        (tmp_path / pattern.format(d=OLD)).write_text("old")
        (tmp_path / pattern.format(d=RECENT)).write_text("recent")
    for name in DURABLE:
        (tmp_path / name).write_text("[]" if name.endswith(".json") else "keep")

    expected = {p.format(d=OLD) for p in TELEMETRY}
    assert {p.name for p in files_to_prune(tmp_path, today=TODAY)} == expected

    removed = clean_localdata(tmp_path, today=TODAY)
    assert {p.name for p in removed} == expected
    for name in DURABLE:
        assert (tmp_path / name).exists(), name
    for pattern in TELEMETRY:
        assert (tmp_path / pattern.format(d=RECENT)).exists()


def test_retention_window_boundary_is_inclusive(tmp_path):
    for day in ("2026-08-26", "2026-08-27", "2026-08-28", "2026-08-29"):
        (tmp_path / f"clv_report_{day}.md").write_text("x")
        (tmp_path / f"picks_{day}.json").write_text("[]")
    removed = clean_localdata(tmp_path, keep_days=3, today=date(2026, 8, 29))
    assert [p.name for p in removed] == ["clv_report_2026-08-26.md"]
    for day in ("2026-08-27", "2026-08-28", "2026-08-29"):
        assert (tmp_path / f"clv_report_{day}.md").exists()
    # Pick archives are durable replay inputs even outside the window.
    assert (tmp_path / "picks_2026-08-26.json").exists()


def test_default_window_is_30_days(tmp_path):
    (tmp_path / "clv_report_2026-08-27.md").write_text("x")   # day 30 of 30
    (tmp_path / "clv_report_2026-08-26.md").write_text("x")   # day 31
    removed = clean_localdata(tmp_path, today=TODAY)
    assert [p.name for p in removed] == ["clv_report_2026-08-26.md"]


def test_dry_run_deletes_nothing(tmp_path):
    (tmp_path / f"clv_report_{OLD}.md").write_text("x")
    removed = clean_localdata(tmp_path, today=TODAY, dry_run=True)
    assert [p.name for p in removed] == [f"clv_report_{OLD}.md"]
    assert (tmp_path / f"clv_report_{OLD}.md").exists()


def test_invalid_window_and_malformed_dates_fail_safe(tmp_path):
    with pytest.raises(ValueError):
        files_to_prune(tmp_path, keep_days=0, today=TODAY)
    (tmp_path / "clv_report_2026-02-31.md").write_text("x")  # not a real date
    assert files_to_prune(tmp_path, today=TODAY) == []


# ---- morning baselines: pruned only when the audit loader proves parity ----

def test_redundant_old_morning_file_is_pruned(tmp_path):
    morning = [_row("A", "B"), _row("C", "D", pick="away")]
    late = _row("E", "F")
    _write(tmp_path / f"picks_morning_{OLD}.json", morning)
    _write(tmp_path / f"picks_{OLD}.json", morning + [late])  # superset, same order

    assert morning_archive_is_redundant(tmp_path, OLD)
    removed = clean_localdata(tmp_path, today=TODAY)
    assert [p.name for p in removed] == [f"picks_morning_{OLD}.json"]
    assert (tmp_path / f"picks_{OLD}.json").exists()


def test_morning_file_is_kept_when_regular_ledger_was_overwritten(tmp_path):
    # A forecast refresh rewrote the regular ledger: the morning file is now
    # the audit's only faithful baseline and removing it would change results.
    _write(tmp_path / f"picks_morning_{OLD}.json", [_row("A", "B", odds=2.1)])
    _write(tmp_path / f"picks_{OLD}.json", [_row("A", "B", odds=2.0), _row("X", "Y")])

    assert not morning_archive_is_redundant(tmp_path, OLD)
    assert clean_localdata(tmp_path, today=TODAY) == []
    assert (tmp_path / f"picks_morning_{OLD}.json").exists()


def test_morning_file_is_kept_when_it_is_the_only_record(tmp_path):
    _write(tmp_path / f"picks_morning_{OLD}.json", [_row("A", "B")])
    assert clean_localdata(tmp_path, today=TODAY) == []
    assert (tmp_path / f"picks_morning_{OLD}.json").exists()


def test_recent_morning_file_is_kept_even_if_redundant(tmp_path):
    rows = [_row("A", "B", date=RECENT)]
    _write(tmp_path / f"picks_morning_{RECENT}.json", rows)
    _write(tmp_path / f"picks_{RECENT}.json", rows)
    assert clean_localdata(tmp_path, today=TODAY) == []


def test_morning_parity_check_failure_keeps_the_file(tmp_path):
    rows = [_row("A", "B")]
    _write(tmp_path / f"picks_morning_{OLD}.json", rows)
    _write(tmp_path / f"picks_{OLD}.json", rows)
    with patch("scripts.clean_localdata._audit_loader", side_effect=ImportError("boom")):
        assert clean_localdata(tmp_path, today=TODAY) == []
    assert (tmp_path / f"picks_morning_{OLD}.json").exists()


def test_pruning_preserves_rolling_audit_input(tmp_path, monkeypatch):
    """End to end: the audit loader over the whole range is unchanged."""
    import scripts.audit_recent_picks as arp

    redundant = [_row("A", "B", date="2026-07-01")]
    _write(tmp_path / "picks_morning_2026-07-01.json", redundant)
    _write(tmp_path / "picks_2026-07-01.json", redundant + [_row("L", "M", date="2026-07-01")])
    _write(tmp_path / "picks_morning_2026-07-02.json", [_row("A", "B", date="2026-07-02", odds=3.0)])
    _write(tmp_path / "picks_2026-07-02.json", [_row("A", "B", date="2026-07-02", odds=1.1)])
    _write(tmp_path / "picks_2026-07-03.json", [_row("Q", "R", date="2026-07-03")])

    before, _ = arp.load_archived_picks_with_receipt("2026-07-01", "2026-07-03", localdata=tmp_path)
    removed = clean_localdata(tmp_path, today=TODAY)
    after, _ = arp.load_archived_picks_with_receipt("2026-07-01", "2026-07-03", localdata=tmp_path)

    assert [p.name for p in removed] == ["picks_morning_2026-07-01.json"]
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True)


def test_cli_main(tmp_path, capsys):
    (tmp_path / f"clv_report_{OLD}.md").write_text("x")
    assert main(["--localdata", str(tmp_path), "--today", TODAY.isoformat()]) == 0
    assert not (tmp_path / f"clv_report_{OLD}.md").exists()
    assert "Removed 1 file(s)" in capsys.readouterr().out


def _private_daily_module():
    """Load scripts/daily.py under a private name.

    test_daily_orchestration registers its own instance as sys.modules
    ["daily"] and patches it by name; re-registering here would swap the
    module out from under those patches.
    """
    import importlib.util
    from pathlib import Path

    script = Path(__file__).resolve().parent.parent / "scripts" / "daily.py"
    spec = importlib.util.spec_from_file_location("daily_cleanup_hook_under_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_daily_pipeline_cleans_before_any_other_step():
    daily = _private_daily_module()
    with patch.object(daily, "sync_repo_state"), \
            patch.object(daily, "run_soft") as run_soft, \
            patch.object(daily, "run"), \
            patch.object(daily, "capture_theodds_snapshot"):
        daily.run_pipeline(target_date="2026-09-25", mode="clv_only")
    first = run_soft.call_args_list[0].args[0]
    assert "scripts/clean_localdata.py" in first
    assert "--keep-days 30" in first and "--today 2026-09-25" in first


def test_shadow_capture_ledgers_are_pruned_on_the_same_clock(tmp_path):
    # Committed as raw evidence since 2026-10-10; every reader is day-scoped,
    # so the standard telemetry window bounds them too.
    old = tmp_path / "betbetter_shadow_2026-06-01.json"
    fresh = tmp_path / "betbetter_shadow_2026-10-10.json"
    other = tmp_path / "sharpapi_odds_shadow_2026-06-01.json"
    for p in (old, fresh, other):
        p.write_text("{}")
    removed = clean_localdata(tmp_path, keep_days=30,
                              today=date(2026, 10, 10))
    assert old in removed and other in removed
    assert fresh.exists()


def test_shadow_like_names_that_are_not_shadow_ledgers_survive(tmp_path):
    tricky = [
        # its own telemetry family with its own pattern; pruned by age, not
        # by the new shadow-ledger patterns — on the 30-day clock it goes,
        # so date it inside the window and assert it survives the run
        "shadow_sent_ledger_2026-10-01.json",
        "scored_candidate_shadow_2026-06-01.jsonl",
        "pinnapi_odds_shadow_2026-06-01.json.bak",  # unknown shape: never delete
        "ml_fade_research_ledger.json",
    ]
    for name in tricky:
        (tmp_path / name).write_text("{}")
    removed = clean_localdata(tmp_path, keep_days=30, today=date(2026, 10, 10))
    assert removed == []


def test_shadow_ledgers_are_deliberately_not_committed():
    # Pre-merge review correction: the 30-day prune bounds the RUNNER WORKING
    # DIRECTORY, not Git history — committing daily shadow payloads would
    # grow repository history indefinitely. Pin the deliberate state: no
    # localdata shadow family may be negated in .gitignore (i.e. tracked)
    # without an explicit size policy, while the prune patterns stay in place.
    import re as _re
    from pathlib import Path as _Path
    from scripts.clean_localdata import TELEMETRY_PATTERNS
    gitignore = (_Path(__file__).resolve().parent.parent / ".gitignore").read_text()
    negated = _re.findall(r"^!localdata/\S*_shadow_20\*\.json$", gitignore, _re.M)
    assert negated == [], f"shadow families must not be committed: {negated}"
    # the runner-side prune (working-directory hygiene) must stay
    pruned = {p.pattern.split("_shadow_")[0][1:]
              for p in TELEMETRY_PATTERNS if "_shadow_" in p.pattern}
    assert len(pruned) == 7, pruned


def test_archive_and_prune_preserves_ledger_cited_odds_cache(tmp_path):
    """Ledger-cited odds cache remains resolvable through archiving and pruning.

    Unrelated, uncited old telemetry retains its standard cleanup behavior.
    """
    repo = tmp_path / "repo"
    localdata = repo / "localdata"
    localdata.mkdir(parents=True)
    docs = repo / "docs" / "operator"
    docs.mkdir(parents=True)
    ledger = docs / "DATED-CLAIMS.md"

    # Old dated odds-cache fixture and a ledger row citing it
    odds_cache_name = f"betexplorer_odds_cache_{OLD}.json"
    odds_cache_path = localdata / odds_cache_name
    odds_payload = b'{"date": "' + OLD.encode() + b'", "fixtures": {"test": 1}}\n'
    odds_cache_path.write_bytes(odds_payload)

    ledger_content = (
        "# Dated claims ledger\n\n"
        "| file | claim | backing |\n"
        "|---|---|---|\n"
        f"| `tests/test_odds.py` | odds verified | `localdata/{odds_cache_name}` |\n"
    )
    ledger.write_text(ledger_content, encoding="utf-8")

    # Unrelated, uncited old telemetry (one pruned by clean_localdata, one archived)
    old_capture = localdata / f"betexplorer_capture_{OLD}.json"
    old_capture.write_text("old capture")
    uncited_odds_name = "betexplorer_odds_cache_2026-07-15.json"
    uncited_odds = localdata / uncited_odds_name
    uncited_odds.write_text("uncited odds")

    # Recent telemetry that should remain untouched
    recent_capture = localdata / f"betexplorer_capture_{RECENT}.json"
    recent_capture.write_text("recent capture")

    # Exercise the archive-and-prune flow via main
    assert main(["--localdata", str(localdata), "--today", TODAY.isoformat()]) == 0

    # Assert the exact cited path still exists with unchanged bytes
    assert odds_cache_path.exists()
    assert odds_cache_path.read_bytes() == odds_payload
    # Ensure it was not moved into archive
    archived_cited = localdata / "archive" / "betexplorer_odds_cache" / "2026" / "08" / odds_cache_name
    assert not archived_cited.exists()

    # Verify unrelated, uncited old telemetry retains its intended cleanup behavior
    assert not old_capture.exists()  # pruned by clean_localdata
    assert not uncited_odds.exists()  # rolled over into archive
    archived_uncited = localdata / "archive" / "betexplorer_odds_cache" / "2026" / "07" / uncited_odds_name
    assert archived_uncited.exists()
    assert archived_uncited.read_text() == "uncited odds"

    # Recent telemetry retains its active state
    assert recent_capture.exists()


def test_prunes_old_timestamped_ml_paper_receipts_and_retains_canonical(tmp_path):
    import clean_localdata as cl
    root = tmp_path / "localdata"
    ml_dir = root / "phase5_reconciliation" / "ml_paper_receipts"
    ml_dir.mkdir(parents=True)

    today = date(2026, 11, 11)
    # Old timestamped receipt (older than 30 days -> prune)
    old_ts = ml_dir / "autobets_ML_2026-10-01_20261001T120000000000Z.json"
    old_ts.write_text("{}")
    # Old canonical receipt (keep)
    old_canonical = ml_dir / "autobets_ML_2026-10-01.json"
    old_canonical.write_text("{}")
    # Fresh timestamped receipt (within 30 days -> keep)
    fresh_ts = ml_dir / "autobets_ML_2026-11-05_20261105T120000000000Z.json"
    fresh_ts.write_text("{}")

    pruned = cl.clean_localdata(root, keep_days=30, today=today)
    assert old_ts in pruned
    assert not old_ts.exists()
    assert old_canonical.exists()
    assert fresh_ts.exists()


def test_old_nonempty_ml_receipts_and_corruption_are_durable_not_telemetry(tmp_path):
    import clean_localdata as cl
    root = tmp_path / "localdata"
    directory = root / "phase5_reconciliation/ml_paper_receipts"
    directory.mkdir(parents=True)
    decision = directory / "autobets_ML_2026-10-01_20261001T120000000000Z.json"
    replacement = directory / "autobets_ML_2026-10-01_20261001T130000000000Z.json"
    corrupt = directory / "autobets_ML_2026-10-01_20261001T140000000000Z.json"
    decision.write_text('{"schema":"autobets_ML_v2","sha256":"original"}')
    replacement.write_text('{"supersession":{"targets":[{"receipt_sha256":"original","acca_index":1}]}}')
    corrupt.write_text('{broken evidence')
    originals = {p: p.read_bytes() for p in (decision, replacement, corrupt)}
    assert cl.clean_localdata(root, keep_days=30, today=date(2026, 11, 13)) == []
    assert all(p.read_bytes() == blob for p, blob in originals.items())
