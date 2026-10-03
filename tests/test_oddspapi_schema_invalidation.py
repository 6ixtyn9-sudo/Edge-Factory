"""OddsPAPI row-generation invalidation (Join-Layer Repair round 2, Task 1).

The 414 rows persisted in ``localdata/oddspapi_odds_2026-10.csv.gz`` on
2026-10-03 came from a parser that read outcome names from the wrong key and
had no fixture identity. Selection reads that monthly file for the rest of
October, so unless those rows are *classified and bypassed* they are re-read
on every subsequent run.

The gate is deliberately on the generation marker rather than on blank
participants: blank teams were only the symptom this generation happened to
show, and a generation-1 row that did carry teams would still have an
untrustworthy selection.

These tests use the raw on-disk row shape as captured, not pre-canonicalised
values.
"""
import csv
import gzip
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import scripts.picks_today as pt  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "capture_oddspapi", ROOT / "scripts" / "capture_oddspapi.py")
capture_oddspapi = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capture_oddspapi)

DAY = "2026-10-03"
CUTOFF = datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc)

# Exactly the on-disk header that produced the 414 corrupt rows: no
# schema_version, and (on the oldest rows) no provider stamp columns either.
GEN1_COLUMNS = ["source", "source_type", "sport", "date", "kickoff", "league",
                "home", "away", "market", "selection", "odds", "bookmaker",
                "captured_at"]


def _gen1_row(**overrides) -> dict:
    """A row in the shape the broken parser actually wrote."""
    row = {
        "source": "oddspapi", "source_type": "odds", "sport": "soccer",
        "date": DAY, "kickoff": f"{DAY}T09:00:00.000Z", "league": "",
        "home": "", "away": "", "market": "1x2", "selection": "home",
        "odds": "4.3", "bookmaker": "bodog.eu",
        "captured_at": f"{DAY}T13:13:33+00:00",
    }
    row.update(overrides)
    return row


def _write(path: Path, rows: list[dict], columns: list[str]) -> None:
    with gzip.open(path, "wt", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in columns})


def _read(path: Path) -> list[dict]:
    with gzip.open(path, "rt", newline="", encoding="utf-8") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


def test_capture_and_selection_agree_on_the_current_generation():
    """A drift between writer and reader would silently blank the lane."""
    assert pt.ODDSPAPI_MIN_SCHEMA_VERSION == capture_oddspapi.SCHEMA_VERSION


def test_old_schema_rows_are_counted_and_bypassed_not_reused(tmp_path, monkeypatch):
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    _write(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz",
           [_gen1_row(odds=o) for o in ("4.3", "4.75", "1.532")], GEN1_COLUMNS)

    stats: dict = {}
    pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["raw_rows"] == 3, "rows must still be OBSERVED, not invisible"
    assert stats["stale_schema_rows"] == 3
    assert stats["usable_rows"] == 0, "a superseded generation is never supply"


def test_a_generation_1_row_with_teams_is_still_refused(tmp_path, monkeypatch):
    """The gate is the generation, not the blank-participant symptom.

    This row would sail past an identity-only check and inject a price whose
    selection the broken parser had already mislabelled.
    """
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    _write(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz",
           [_gen1_row(home="Croatia", away="England", league="UEFA Nations League")],
           GEN1_COLUMNS)

    stats: dict = {}
    pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["stale_schema_rows"] == 1
    assert stats["identity_missing_rows"] == 0, "refused on generation, not symptom"
    assert stats["usable_rows"] == 0


def test_current_generation_rows_are_consumed_normally(tmp_path, monkeypatch):
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    _write(
        tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz",
        [_gen1_row(home="Croatia", away="England", selection="away", odds="1.78",
                   league="UEFA Nations League",
                   schema_version=capture_oddspapi.SCHEMA_VERSION)],
        capture_oddspapi.COLUMNS,
    )

    stats: dict = {}
    pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["stale_schema_rows"] == 0
    assert stats["usable_rows"] == 1


def test_mixed_file_keeps_only_the_current_generation(tmp_path, monkeypatch):
    """The real October file will hold both once capture runs again."""
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    rows = [_gen1_row(odds=o) for o in ("4.3", "4.75", "1.532")]
    rows.append(_gen1_row(home="Croatia", away="England", selection="away",
                          odds="1.78", league="UEFA Nations League",
                          schema_version=capture_oddspapi.SCHEMA_VERSION))
    _write(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz", rows,
           capture_oddspapi.COLUMNS)

    stats: dict = {}
    bundle = pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["raw_rows"] == 4
    assert stats["stale_schema_rows"] == 3
    assert stats["usable_rows"] == 1

    report = pt.donor_join_diagnostics(
        [{"date": DAY, "home": "Croatia", "away": "England",
          "market": "1x2", "pick": "away"}],
        [bundle],
    )[pt.ODDSPAPI_ODDS_SOURCE]
    assert report["miss_counts"].get("stale_schema") == 3
    assert report["matched_rows"] == 1, "the good row must still join"


def test_the_evidence_file_is_never_rewritten_or_deleted(tmp_path, monkeypatch):
    """Bypass must not mutate the capture. The corrupt rows are evidence."""
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    path = tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz"
    _write(path, [_gen1_row(odds=o) for o in ("4.3", "4.75")], GEN1_COLUMNS)
    before = path.read_bytes()

    pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats={})

    assert path.exists()
    assert path.read_bytes() == before


def test_capture_stamps_every_written_row(tmp_path, monkeypatch):
    monkeypatch.setattr(capture_oddspapi, "OUT_DIR", tmp_path)
    added = capture_oddspapi._append_rows(
        [{k: v for k, v in _gen1_row(home="Croatia", away="England").items()}], DAY)
    assert added == 1
    written = _read(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz")
    assert [r["schema_version"] for r in written] == [
        str(capture_oddspapi.SCHEMA_VERSION)]


def test_migration_widens_the_header_without_back_stamping_old_rows(tmp_path, monkeypatch):
    """Old rows must not inherit the new generation by being migrated."""
    monkeypatch.setattr(capture_oddspapi, "OUT_DIR", tmp_path)
    path = tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz"
    _write(path, [_gen1_row(odds="4.3")], GEN1_COLUMNS)

    capture_oddspapi._append_rows(
        [_gen1_row(home="Croatia", away="England", selection="away", odds="1.78")],
        DAY)

    written = _read(path)
    assert len(written) == 2, "no row dropped by migration"
    assert written[0]["schema_version"] == "", "pre-existing row stays unmarked"
    assert written[0]["odds"] == "4.3", "no value changed by migration"
    assert written[1]["schema_version"] == str(capture_oddspapi.SCHEMA_VERSION)


def test_a_corrected_row_is_not_deduped_away_by_its_broken_predecessor(tmp_path, monkeypatch):
    """Invalidation beats idempotence: the generation is in the dedupe key."""
    monkeypatch.setattr(capture_oddspapi, "OUT_DIR", tmp_path)
    identical_except_generation = _gen1_row(odds="4.3")
    _write(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz",
           [identical_except_generation], GEN1_COLUMNS)

    added = capture_oddspapi._append_rows([dict(identical_except_generation)], DAY)

    assert added == 1, "a re-captured row must not be suppressed by a stale one"


def test_rerunning_the_current_generation_still_dedupes(tmp_path, monkeypatch):
    """The F7 idempotence guarantee must survive the new column."""
    monkeypatch.setattr(capture_oddspapi, "OUT_DIR", tmp_path)
    row = _gen1_row(home="Croatia", away="England", selection="away", odds="1.78")
    assert capture_oddspapi._append_rows([dict(row)], DAY) == 1
    assert capture_oddspapi._append_rows([dict(row)], DAY) == 0


@pytest.mark.parametrize("marker", ["", None, "1", "not-a-number", "0"])
def test_any_pre_generation_marker_is_refused(tmp_path, monkeypatch, marker):
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    _write(tmp_path / f"oddspapi_odds_{DAY[:7]}.csv.gz",
           [_gen1_row(home="Croatia", away="England", schema_version=marker)],
           capture_oddspapi.COLUMNS)

    stats: dict = {}
    pt.oddspapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["usable_rows"] == 0
    assert stats["stale_schema_rows"] == 1


def test_other_providers_are_not_gated_on_oddspapi_generation(tmp_path, monkeypatch):
    """The Odds API shares the reader but has no generation defect."""
    monkeypatch.setattr(pt, "LOCALDATA", tmp_path)
    _write(
        tmp_path / f"theoddsapi_odds_{DAY[:7]}.csv.gz",
        [_gen1_row(source="theoddsapi", home="Croatia", away="England",
                   selection="away", odds="1.78")],
        GEN1_COLUMNS,
    )

    stats: dict = {}
    pt.theoddsapi_odds_bundle(DAY, not_after=CUTOFF, stats=stats)

    assert stats["usable_rows"] == 1
    assert stats["stale_schema_rows"] == 0
