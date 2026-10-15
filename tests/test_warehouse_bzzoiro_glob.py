"""The bzzoiro warehouse view must read monthly predictions only, never bzzoiro_odds."""

from __future__ import annotations

import glob
import gzip
import os

import pytest

from edgefactory import warehouse


def _write_gz(path, text):
    with gzip.open(path, "wt") as fh:
        fh.write(text)


@pytest.fixture
def localdata(tmp_path):
    _write_gz(tmp_path / "bzzoiro_2026-09.csv.gz", "date,home,away,p1\n2026-09-01,A,B,40.0\n")
    _write_gz(tmp_path / "bzzoiro_2026-10.csv.gz", "date,home,away,p1\n2026-10-01,C,D,50.0\n")
    _write_gz(
        tmp_path / "bzzoiro_odds_2026-09.csv.gz",
        "source,source_type,sport,date,kickoff,league,home,away,market,selection,odds,bookmaker,captured_at\n"
        "bzzoiro,odds,soccer,2026-09-30,2026-09-30T02:00:00Z,L,A,B,ou_2.5,under,1.78,sbo,2026-09-30T01:54:53Z\n",
    )
    return tmp_path


def test_pattern_constant_is_the_exact_monthly_form():
    assert warehouse.BZZOIRO_MONTHLY_GLOB == "bzzoiro_[0-9][0-9][0-9][0-9]-[0-9][0-9].csv.gz"


def test_python_glob_matches_monthly_files_only(localdata):
    matched = sorted(os.path.basename(p) for p in glob.glob(f"{localdata}/{warehouse.BZZOIRO_MONTHLY_GLOB}"))
    assert matched == ["bzzoiro_2026-09.csv.gz", "bzzoiro_2026-10.csv.gz"]


def test_duckdb_reader_matches_monthly_files_only(localdata):
    duckdb = pytest.importorskip("duckdb")
    con = duckdb.connect()
    rows = con.execute(
        f"SELECT DISTINCT regexp_extract(filename, '[^/]+$') FROM read_csv_auto("
        f"'{localdata}/{warehouse.BZZOIRO_MONTHLY_GLOB}', all_varchar=true, union_by_name=true, filename=true)"
    ).fetchall()
    assert sorted(r[0] for r in rows) == ["bzzoiro_2026-09.csv.gz", "bzzoiro_2026-10.csv.gz"]
