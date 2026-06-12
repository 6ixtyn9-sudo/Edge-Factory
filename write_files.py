import os
from pathlib import Path

files = {
    "scripts/local_backfill.py": r'''#!/usr/bin/env python3
"""
local_backfill.py — Supabase-free historical backfill to monthly CSV.gz.
Resumable via state file. Works with simple module sources (fetch_day -> list[dict]).

python3 scripts/local_backfill.py forebet 2024-01-01 2026-06-11 --max-seconds 1500
python3 scripts/local_backfill.py statarea 2017-01-01 2023-12-31 --max-seconds 1500
"""
from __future__ import annotations
import csv
import gzip
import importlib
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
LOCALDATA.mkdir(exist_ok=True)

def load_source(key: str):
    try:
        return importlib.import_module(f"edgefactory.sources.{key}")
    except ModuleNotFoundError as e:
        print(f"ERROR: source '{key}' not found", file=sys.stderr)
        sys.exit(2)

def dedup_key(row: dict, columns: list[str]):
    # Prefer event_id if present
    if "event_id" in row and row.get("event_id"):
        return str(row["event_id"])
    # fallback: date + home + away
    return (
        str(row.get("date", "")),
        str(row.get("home", "")).lower(),
        str(row.get("away", "")).lower(),
    )

def read_existing(path: Path):
    if not path.exists():
        return {}
    try:
        with gzip.open(path, "rt", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            # build key map
            out = {}
            for r in rows:
                k = dedup_key(r, reader.fieldnames or [])
                out[k] = r
            return out
    except Exception:
        return {}

def main():
    if len(sys.argv) < 4:
        print("usage: local_backfill.py <source> <start YYYY-MM-DD> <end YYYY-MM-DD> [--max-seconds N] [--workers N]", file=sys.stderr)
        sys.exit(2)

    source_key, start_s, end_s = sys.argv[1], sys.argv[2], sys.argv[3]
    max_seconds = 10**9
    if "--max-seconds" in sys.argv:
        max_seconds = int(sys.argv[sys.argv.index("--max-seconds") + 1])
    # --workers is accepted for compatibility with capture_daily, ignored (single-process)

    sys.path.insert(0, str(ROOT / "src"))
    mod = load_source(source_key)

    if not hasattr(mod, "fetch_day"):
        print(f"ERROR: {source_key} has no fetch_day()", file=sys.stderr)
        sys.exit(2)

    columns = getattr(mod, "COLUMNS", None)
    if not columns:
        print(f"WARNING: {source_key} has no COLUMNS, will infer from first row", file=sys.stderr)

    state_path = LOCALDATA / f"state_{source_key}.json"
    done = set()
    if state_path.exists():
        try:
            done = set(json.loads(state_path.read_text()).get("done", []))
        except Exception:
            pass

    start, end = date.fromisoformat(start_s), date.fromisoformat(end_s)
    todo = []
    d = start
    while d <= end:
        if d.isoformat() not in done:
            todo.append(d)
        d += timedelta(days=1)

    print(f"{source_key}: {len(todo)} days to fetch ({len(done)} done)")

    t0 = time.time()
    buf: dict[str, list[dict]] = {}
    n = 0

    def flush():
        for month, rows in buf.items():
            if not rows:
                continue
            path = LOCALDATA / f"{source_key}_{month}.csv.gz"
            existing = read_existing(path)
            # merge
            file_columns = columns or sorted({k for r in rows for k in r.keys()})
            for r in rows:
                k = dedup_key(r, file_columns)
                # stringify all values for csv
                existing[k] = {col: "" if r.get(col) is None else str(r.get(col, "")) for col in file_columns}
            # write
            with gzip.open(path, "wt", newline="", compresslevel=6) as f:
                w = csv.DictWriter(f, fieldnames=file_columns)
                w.writeheader()
                for row in sorted(existing.values(), key=lambda x: (x.get("date",""), x.get("home",""), x.get("away",""))):
                    w.writerow(row)
        buf.clear()
        state_path.write_text(json.dumps({"done": sorted(done)}))

    try:
        for d in todo:
            if time.time() - t0 > max_seconds:
                print("time budget hit — flushing (resumable)")
                break
            try:
                rows = mod.fetch_day(d.isoformat())
                if rows:
                    # ensure date field is set
                    for r in rows:
                        if "date" not in r or not r["date"]:
                            r["date"] = d.isoformat()
                    month = d.strftime("%Y-%m")
                    buf.setdefault(month, []).extend(rows)
                done.add(d.isoformat())
                n += 1
                if n % 10 == 0:
                    flush()
                    el = time.time() - t0
                    print(f"  {d} | {n}/{len(todo)} | {el:.0f}s | ~{el/n:.1f}s/day")
            except Exception as e:
                msg = repr(e)
                # permanently gone?
                if "410" in msg or "404" in msg or "Gone" in msg:
                    done.add(d.isoformat())
                else:
                    print(f"  {d} FAILED: {e}")
                    # don't mark done, retry next run
        flush()
    finally:
        pass

    print(f"done this run: {n} days in {time.time()-t0:.0f}s; total {len(done)}")

if __name__ == "__main__":
    main()
''',
    "src/edgefactory/warehouse.py": r'''"""DuckDB analytics layer.

DuckDB = "SQLite for analytics": a zero-server, single-file (or in-memory)
SQL engine that reads csv.gz/parquet directly and crunches millions of rows
in milliseconds. Supabase stays the system-of-record for edges/picks/live ops;
DuckDB is where ALL mining and backtesting happens.

Usage:
from edgefactory.warehouse import connect
con = connect() # views: forebet, zulubet, statarea, consensus2, consensus3
con.sql("SELECT count(*) FROM statarea").show()
"""
from __future__ import annotations

from pathlib import Path

import duckdb

from .util import norm_team_sql

ROOT = Path(__file__).resolve().parent.parent.parent
LOCALDATA = ROOT / "localdata"

def _prob(col: str) -> str:
    """Cast probability column: NaN -> NULL, 0 allowed."""
    return (
        f"CASE WHEN isnan(TRY_CAST({col} AS DOUBLE)) THEN NULL "
        f"ELSE TRY_CAST({col} AS DOUBLE) END"
    )

def _odds(col: str) -> str:
    """Cast odds column: NaN -> NULL, and odds <= 1.0 are junk -> NULL."""
    return (
        f"CASE WHEN isnan(TRY_CAST({col} AS DOUBLE)) "
        f"OR TRY_CAST({col} AS DOUBLE) <= 1.0 THEN NULL "
        f"ELSE TRY_CAST({col} AS DOUBLE) END"
    )

def _src_view(con, name: str, glob: str, select: str) -> None:
    con.execute(
        f"CREATE OR REPLACE VIEW {name} AS SELECT {select} "
        f"FROM read_csv_auto('{glob}', all_varchar=true, union_by_name=true)"
    )

def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False

def connect(db: str | None = None) -> duckdb.DuckDBPyConnection:
    """Open DuckDB (in-memory by default) with all source views + join keys."""
    import glob as _glob
    con = duckdb.connect(db or ":memory:")
    nh, na = norm_team_sql("home"), norm_team_sql("away")
    common = (
        f"date, home, away, {nh} AS hkey, {na} AS akey, "
        "TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs, "
        f"{_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2"
    )
    if _glob.glob(f"{LOCALDATA}/forebet.csv.gz"):
        _src_view(
            con, "forebet", f"{LOCALDATA}/forebet.csv.gz",
            common + f", {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx,"
            f" {_odds('odd2')} AS odd2,"
            " TRY_CAST(ht_hs AS INT) AS ht_hs, TRY_CAST(ht_gs AS INT) AS ht_gs,"
            f" {_prob('p_under')} AS p_under, {_prob('p_over')} AS p_over,"
            f" {_odds('odd_under')} AS odd_under, {_odds('odd_over')} AS odd_over,"
            f" {_prob('p_gg')} AS p_gg, {_prob('p_ng')} AS p_ng,"
            f" {_odds('odd_gg')} AS odd_gg, {_odds('odd_ng')} AS odd_ng,"
            " league, status",
        )
    if _glob.glob(f"{LOCALDATA}/zulubet.csv.gz"):
        _src_view(
            con, "zulubet", f"{LOCALDATA}/zulubet.csv.gz",
            common + f", {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx,"
            f" {_odds('odd2')} AS odd2, tip, league",
        )
    if _glob.glob(f"{LOCALDATA}/statarea.csv.gz"):
        _src_view(
            con, "statarea", f"{LOCALDATA}/statarea.csv.gz",
            common + ", TRY_CAST(ht_hs AS INT) AS ht_hs, TRY_CAST(ht_gs AS INT) AS ht_gs,"
            f" {_prob('p1_ht')} AS p1_ht, {_prob('px_ht')} AS px_ht,"
            f" {_prob('p2_ht')} AS p2_ht,"
            f" {_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25,"
            f" {_prob('p_o35')} AS p_o35, tip, league",
        )

    # settled-only convenience views with outcome + each model's top pick
    pick = (
        "CASE WHEN p1 >= px AND p1 >= p2 THEN 'home' "
        "WHEN p2 >= px THEN 'away' ELSE 'draw' END"
    )
    outcome = (
        "CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away' ELSE 'draw' END"
    )
    for v in ("forebet", "zulubet", "statarea"):
        if _table_exists(con, v):
            con.execute(
                f"CREATE OR REPLACE VIEW {v}_settled AS "
                f"SELECT *, {pick} AS pick, GREATEST(p1, px, p2) AS pmax, {outcome} AS outcome "
                f"FROM {v} WHERE hs IS NOT NULL AND gs IS NOT NULL "
                f"AND p1 IS NOT NULL AND px IS NOT NULL AND p2 IS NOT NULL"
            )

    # predictz: categorical picks + odds (no probs). Settled by joining scores
    # from forebet (results donor) on (date, hkey, akey).
    if _glob.glob(f"{LOCALDATA}/predictz_*.csv.gz"):
        _src_view(
            con, "predictz_raw", f"{LOCALDATA}/predictz_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, pick, pred_score,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2",
        )
        con.execute("""
            CREATE OR REPLACE VIEW predictz_settled AS
            WITH pz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM predictz_raw
                        WHERE pick IS NOT NULL),
                 fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                        FROM forebet WHERE hs IS NOT NULL)
            SELECT pz.*, fb.hs, fb.gs,
                   CASE WHEN fb.hs > fb.gs THEN 'home'
                        WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome,
                   CASE pz.pick WHEN 'home' THEN pz.odd1
                                WHEN 'draw' THEN pz.oddx ELSE pz.odd2 END AS pick_odds
            FROM pz JOIN fb USING (date, hkey, akey)
            WHERE length(pz.hkey) >= 4 AND length(pz.akey) >= 4
        """)

    if _glob.glob(f"{LOCALDATA}/scoutingstats_*.csv.gz"):
        _src_view(
            con, "scoutingstats", f"{LOCALDATA}/scoutingstats_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, country, status,"
            " TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs,"
            f" {_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2,"
            f" {_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25,"
            f" {_prob('p_o35')} AS p_o35, {_prob('p_gg')} AS p_gg, {_prob('p_ng')} AS p_ng,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2,"
            f" {_odds('odd_o25')} AS odd_o25, {_odds('odd_u25')} AS odd_u25,"
            f" {_odds('odd_gg')} AS odd_gg, {_odds('odd_ng')} AS odd_ng",
        )
        con.execute("""
            CREATE OR REPLACE VIEW scoutingstats_settled AS
            SELECT *,
                   CASE WHEN p1 >= px AND p1 >= p2 THEN 'home'
                        WHEN p2 >= px THEN 'away' ELSE 'draw' END AS pick,
                   GREATEST(p1, px, p2) AS pmax,
                   CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away'
                        ELSE 'draw' END AS outcome
            FROM scoutingstats
            WHERE hs IS NOT NULL AND p1 IS NOT NULL AND px IS NOT NULL
              AND p2 IS NOT NULL
        """)

    if _glob.glob(f"{LOCALDATA}/bettingclosed_*.csv.gz"):
        _src_view(
            con, "bettingclosed", f"{LOCALDATA}/bettingclosed_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey,"
            " TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs,"
            f" {_odds('odd1')} AS odd1, {_odds('oddx')} AS oddx, {_odds('odd2')} AS odd2,"
            f" {_odds('odd_under')} AS odd_under, {_odds('odd_over')} AS odd_over,"
            " lower(pick_1x2) AS pick_1x2,"
            f" {_odds('odd_pick_1x2')} AS odd_pick_1x2,"
            " lower(pick_ou) AS pick_ou,"
            f" {_odds('odd_pick_ou')} AS odd_pick_ou,"
            " lower(pick_btts) AS pick_btts,"
            f" {_odds('odd_pick_btts')} AS odd_pick_btts",
        )
        con.execute("""
            CREATE OR REPLACE VIEW bettingclosed_settled AS
            SELECT *,
                CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away'
                     ELSE 'draw' END AS outcome,
                -- 1x2 picks incl. double chance: 1, x, 2, 1x, 12, x2
                CASE pick_1x2
                  WHEN '1'  THEN (hs > gs)
                  WHEN '2'  THEN (hs < gs)
                  WHEN 'x'  THEN (hs = gs)
                  WHEN '1x' THEN (hs >= gs)
                  WHEN 'x2' THEN (hs <= gs)
                  WHEN '12' THEN (hs != gs)
                END AS won_1x2,
                CASE
                  WHEN pick_ou LIKE 'over%'  THEN (hs + gs >= 3)
                  WHEN pick_ou LIKE 'under%' THEN (hs + gs <= 2)
                END AS won_ou,
                CASE pick_btts
                  WHEN 'gol'   THEN (hs > 0 AND gs > 0)
                  WHEN 'nogol' THEN (hs = 0 OR gs = 0)
                END AS won_btts
            FROM bettingclosed
            WHERE hs IS NOT NULL AND gs IS NOT NULL
              AND length(hkey) >= 4 AND length(akey) >= 4
        """)

    # ---- additional 6 sources (vitibet, afootballreport, betclan, freesupertips, windrawwin, bzzoiro) ----
    # vitibet: 1x2 probs are % (0-100), convert to 0-1 for consistency
    if _glob.glob(f"{LOCALDATA}/vitibet_*.csv.gz"):
        def _p100(col): return f"TRY_CAST({col} AS DOUBLE)/100.0"
        _src_view(
            con, "vitibet", f"{LOCALDATA}/vitibet_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "TRY_CAST(hs AS INT) AS hs, TRY_CAST(gs AS INT) AS gs, "
            f"{_p100('p1')} AS p1, {_p100('px')} AS px, {_p100('p2')} AS p2, "
            "tip, pred_hs, pred_gs, status, kickoff"
        )
        con.execute(f"""
            CREATE OR REPLACE VIEW vitibet_settled AS
            SELECT *, {pick} AS pick, GREATEST(p1, px, p2) AS pmax, {outcome} AS outcome
            FROM vitibet WHERE hs IS NOT NULL AND gs IS NOT NULL
              AND p1 IS NOT NULL AND px IS NOT NULL AND p2 IS NOT NULL
        """)

    # betclan: 1x2 probs are % (0-100)
    if _glob.glob(f"{LOCALDATA}/betclan_*.csv.gz"):
        def _p100(col): return f"TRY_CAST({col} AS DOUBLE)/100.0"
        _src_view(
            con, "betclan", f"{LOCALDATA}/betclan_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, "
            f"{_p100('p1')} AS p1, {_p100('px')} AS px, {_p100('p2')} AS p2, "
            "winner, match_id, url"
        )

    # bzzoiro: ML model, probs are 0-1, includes xG and OU probs
    if _glob.glob(f"{LOCALDATA}/bzzoiro_*.csv.gz"):
        _src_view(
            con, "bzzoiro", f"{LOCALDATA}/bzzoiro_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, event_id, "
            f"{_prob('p1')} AS p1, {_prob('px')} AS px, {_prob('p2')} AS p2, "
            f"{_prob('p_o15')} AS p_o15, {_prob('p_o25')} AS p_o25, {_prob('p_o35')} AS p_o35, "
            f"{_prob('p_gg')} AS p_gg, "
            "TRY_CAST(xg_home AS DOUBLE) AS xg_home, TRY_CAST(xg_away AS DOUBLE) AS xg_away, "
            "predicted, pred_score, rec_bet_favorite, rec_winner, "
            "TRY_CAST(confidence AS DOUBLE) AS confidence, model_version, kickoff, captured_at"
        )

    # freesupertips: tipster picks with odds/confidence, no 1x2 probs
    if _glob.glob(f"{LOCALDATA}/freesupertips_*.csv.gz"):
        _src_view(
            con, "freesupertips", f"{LOCALDATA}/freesupertips_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "tip, " + _odds('odds') + " AS odds, "
            "TRY_CAST(confidence AS INT) AS confidence, stake, kickoff"
        )

    # afootballreport: streak-based OU/BTTS tips, pseudo_prob 0-1
    if _glob.glob(f"{LOCALDATA}/afootballreport_*.csv.gz"):
        _src_view(
            con, "afootballreport", f"{LOCALDATA}/afootballreport_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "market, tip, "
            "TRY_CAST(streak_pct AS INT) AS streak_pct, "
            "TRY_CAST(streak_n AS INT) AS streak_n, "
            f"{_prob('pseudo_prob')} AS pseudo_prob, kickoff"
        )

    # windrawwin: categorical pick + stake confidence
    if _glob.glob(f"{LOCALDATA}/windrawwin_*.csv.gz"):
        _src_view(
            con, "windrawwin", f"{LOCALDATA}/windrawwin_*.csv.gz",
            f"date, home, away, {nh} AS hkey, {na} AS akey, league, "
            "lower(pick) AS pick, stake, pred_score"
        )

    # 2-way consensus: forebet x zulubet
    if _table_exists(con, "forebet_settled") and _table_exists(con, "zulubet_settled"):
        con.execute("""
            CREATE OR REPLACE VIEW consensus2 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled)
            SELECT fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS fb_pick, zb.pick AS zb_pick,
                   fb.pmax AS fb_p, zb.pmax AS zb_p,
                   (fb.pmax + zb.pmax)/2 AS avg_p,
                   fb.odd1, fb.oddx, fb.odd2,
                   CASE fb.pick WHEN 'home' THEN fb.odd1
                                WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds
            FROM fb JOIN zb USING (date, hkey, akey)
            WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
        """)

    # 3-way consensus: + statarea
    if _table_exists(con, "forebet_settled") and _table_exists(con, "zulubet_settled") and _table_exists(con, "statarea_settled"):
        con.execute("""
            CREATE OR REPLACE VIEW consensus3 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                 sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled)
            SELECT fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS fb_pick, zb.pick AS zb_pick, sa.pick AS sa_pick,
                   fb.pmax AS fb_p, zb.pmax AS zb_p, sa.pmax AS sa_p,
                   (fb.pmax + zb.pmax + sa.pmax)/3 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1
                                WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds
            FROM fb JOIN zb USING (date, hkey, akey)
                    JOIN sa USING (date, hkey, akey)
            WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
        """)
    return con
''',
    "scripts/build_warehouse.py": r'''#!/usr/bin/env python3
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
''',
    "supabase/migrations/0005_all_sources.sql": r'''-- ============================================================
-- 0005_all_sources.sql — register remaining 6 adapters (12 total)
-- ============================================================
insert into sources (key, kind, base_url) values
('predictz', 'predictions', 'https://www.predictz.com'),
('windrawwin', 'predictions', 'https://www.windrawwin.com'),
('betclan', 'predictions', 'https://www.betclan.com'),
('freesupertips', 'predictions', 'https://www.freesupertips.com'),
('bettingclosed', 'predictions', 'https://www.bettingclosed.com'),
('bzzoiro', 'predictions', 'https://sports.bzzoiro.com')
on conflict (key) do nothing;

-- bzzoiro is a real ML model API (CatBoost, xG)
-- Auth: Authorization: Token <key>
-- Endpoint: /api/v2/predictions/
-- Provides: p1/px/p2, xg_home/xg_away, p_o15/p_o25/p_o35, p_gg, pred_score, confidence, model_version
-- Capture-forward: snapshot ALL upcoming daily; settle later via /api/v2/events/
'''
}

for path_str, content in files.items():
    p = Path(path_str)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
