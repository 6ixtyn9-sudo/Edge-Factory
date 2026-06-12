#!/usr/bin/env python3
"""Materialize localdata/*.csv.gz into a single fast DuckDB file.

python3 scripts/build_warehouse.py            # -> localdata/warehouse.duckdb
Run after any backfill. Queries go from ~20s (re-parsing gzip CSVs) to ~ms.
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb # noqa: E402

from edgefactory.warehouse import connect # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"

TABLES = [
    "forebet_settled",
    "zulubet_settled",
    "statarea_settled",
    "predictz_settled",
    "scoutingstats_settled",
    "bettingclosed_settled",
    "vitibet_settled",
    # raw (unsettled) sources – still materialize for fast picks
    "vitibet",
    "betclan",
    "bzzoiro",
    "freesupertips",
    "afootballreport",
    "windrawwin",
    "consensus2",
    "consensus3",
]

def main() -> None:
    t0 = time.time()
    src = connect() # in-memory with views over csv.gz
    if DB.exists():
        DB.unlink()
    out = duckdb.connect(str(DB))
    out.close()
    # ATTACH the file DB from the in-memory connection and copy tables across
    src.execute(f"ATTACH '{DB}' AS wh")
    for t in TABLES:
        try:
            src.execute(f"CREATE TABLE wh.{t} AS SELECT * FROM {t}")
            n = src.sql(f"SELECT count(*) FROM wh.{t}").fetchone()[0]
            print(f" {t}: {n:,} rows")
        except Exception as e:
            print(f" {t}: skipped ({type(e).__name__}: {str(e)[:80]})")
    src.execute("DETACH wh")
    print(f"warehouse built in {time.time()-t0:.1f}s -> {DB} "
          f"({DB.stat().st_size/1e6:.0f} MB)")

if __name__ == "__main__":
    main()
