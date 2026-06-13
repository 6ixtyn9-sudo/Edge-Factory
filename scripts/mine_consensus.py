#!/usr/bin/env python3
"""Walk-forward consensus miner on the DuckDB warehouse.

Re-validates the certified rules and scans the threshold grid, all with the
standard gates (no mini-backtests, Wilson LB, ROI alongside hit rate).

    python3 scripts/mine_consensus.py --split 2025-06-01
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb  # noqa: E402

from edgefactory.assay import wilson_lb  # noqa: E402
from edgefactory.config import GATES  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
OUT = ROOT / "localdata" / "edges_consensus.json"


def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False

def get_scale(con, view):
    try:
        max_p = con.sql(f"SELECT max(p1) FROM {view}").fetchone()[0]
        if max_p is not None and float(max_p) > 1.5:
            return 100.0
        return 1.0
    except Exception:
        return 1.0

def stats(con, view, where, split, period):
    cmp = "<" if period == "train" else ">="
    q = f"""
        SELECT count(*) n,
               sum(CASE WHEN pick = outcome THEN 1 ELSE 0 END) wins,
               avg(pick_odds) avg_odds,
               sum(CASE WHEN pick_odds IS NOT NULL THEN
                     CASE WHEN pick = outcome THEN pick_odds - 1 ELSE -1 END
                   ELSE 0 END) pnl,
               sum(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
        FROM {view} WHERE ({where}) AND date {cmp} '{split}'
    """
    n, wins, avg_odds, pnl, n_priced = con.sql(q).fetchone()
    n, wins = int(n or 0), int(wins or 0)
    hit = wins / n if n else 0.0
    roi = (pnl / n_priced) if n_priced else None
    return {
        "n": n, "wins": wins, "hit": round(hit, 4),
        "wilson_lb": round(wilson_lb(wins, n), 4),
        "avg_odds": round(avg_odds, 3) if avg_odds else None,
        "roi": round(roi, 4) if roi is not None else None,
        "n_priced": int(n_priced or 0),
    }


def evaluate(con, name, view, where, split, market="1x2"):
    tr = stats(con, view, where, split, "train")
    va = stats(con, view, where, split, "valid")
    certified = (
        tr["n"] >= GATES.min_n_train
        and va["n"] >= GATES.min_n_valid
        and (tr["roi"] is None or tr["roi"] >= GATES.min_roi_train)
        and (va["roi"] is None or va["roi"] >= GATES.min_roi_valid)
        and va["wilson_lb"] >= 0.5
    )
    return {"rule": name, "view": view, "where": where, "market": market,
            "train": tr, "valid": va,
            "status": "certified" if certified else "candidate"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default=GATES.walkforward_split)
    args = ap.parse_args()

    if not DB.exists():
        print("Warehouse does not exist, exiting gracefully.")
        OUT.parent.mkdir(exist_ok=True)
        OUT.write_text(json.dumps({"split": args.split, "gates": vars(GATES), "edges": []}, indent=2))
        return

    con = duckdb.connect(str(DB), read_only=True)
    results = []
    
    has_fb = _table_exists(con, "forebet_settled")
    has_zb = _table_exists(con, "zulubet_settled")
    has_sa = _table_exists(con, "statarea_settled")
    has_vb = _table_exists(con, "vitibet_settled")
    has_ss = _table_exists(con, "scoutingstats_settled")
    has_betclan = _table_exists(con, "betclan")
    has_bzzoiro = _table_exists(con, "bzzoiro")

    scales = {}
    for v in ["forebet_settled", "zulubet_settled", "statarea_settled", "vitibet_settled", "scoutingstats_settled", "betclan", "bzzoiro"]:
        if _table_exists(con, v):
            scales[v] = get_scale(con, v)
        else:
            scales[v] = 1.0

    if has_betclan and has_fb:
        con.execute("""
            CREATE OR REPLACE TEMP VIEW betclan_settled AS
            WITH bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan),
                 fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                        FROM forebet_settled)
            SELECT bc.*, fb.hs, fb.gs,
                   CASE WHEN bc.p1 >= bc.px AND bc.p1 >= bc.p2 THEN 'home'
                        WHEN bc.p2 >= bc.px THEN 'away' ELSE 'draw' END AS pick,
                   GREATEST(bc.p1, bc.px, bc.p2) AS pmax,
                   CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome
            FROM bc JOIN fb USING (date, hkey, akey)
        """)
        has_betclan_settled = True
        scales["betclan_settled"] = scales["betclan"]
    else:
        has_betclan_settled = False

    if has_bzzoiro and has_fb:
        con.execute("""
            CREATE OR REPLACE TEMP VIEW bzzoiro_settled AS
            WITH bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro),
                 fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                        FROM forebet_settled)
            SELECT bz.*, fb.hs, fb.gs,
                   CASE WHEN bz.p1 >= bz.px AND bz.p1 >= bz.p2 THEN 'home'
                        WHEN bz.p2 >= bz.px THEN 'away' ELSE 'draw' END AS pick,
                   GREATEST(bz.p1, bz.px, bz.p2) AS pmax,
                   CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome
            FROM bz JOIN fb USING (date, hkey, akey)
        """)
        has_bzzoiro_settled = True
        scales["bzzoiro_settled"] = scales["bzzoiro"]
    else:
        has_bzzoiro_settled = False

    if has_fb and has_zb:
        con.execute("""
            CREATE OR REPLACE TEMP VIEW v_consensus2 AS
            SELECT *, fb_pick AS pick FROM consensus2
        """)
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        
        for thr in (60, 65, 70, 75, 80):
            results.append(evaluate(
                con, f"2way-unanimous avg_p>={thr}", "v_consensus2",
                f"fb_pick = zb_pick AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}", args.split))
                
        results.append(evaluate(
            con, "VETO-CHECK disagree, follow forebet", "v_consensus2",
            "fb_pick != zb_pick", args.split))
            
        for thr in (65, 70):
            results.append(evaluate(
                con, f"2way-unanimous no-draw avg_p>={thr}", "v_consensus2",
                f"fb_pick = zb_pick AND fb_pick != 'draw' AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                args.split))

    if has_fb and has_zb and has_sa:
        con.execute("""
            CREATE OR REPLACE TEMP VIEW v_consensus3 AS
            SELECT *, fb_pick AS pick FROM consensus3
        """)
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"3way-unanimous avg_p>={thr}", "v_consensus3",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                args.split))

    if has_fb and has_zb and has_sa and has_vb:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        svb = scales["vitibet_settled"]
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW consensus4 AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                 sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled),
                 vb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM vitibet_settled)
            SELECT fb.date, fb.outcome,
                   fb.pick AS pick, fb.pick AS fb_pick, zb.pick AS zb_pick, sa.pick AS sa_pick, vb.pick AS vb_pick,
                   ((fb.pmax/{sfb} + zb.pmax/{szb} + sa.pmax/{ssa} + vb.pmax/{svb})/4)*100 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds
            FROM fb JOIN zb USING (date, hkey, akey)
                    JOIN sa USING (date, hkey, akey)
                    JOIN vb USING (date, hkey, akey)
        """)
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"4way-unanimous-vb avg_p>={thr}", "consensus4",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND sa_pick = vb_pick AND avg_p >= {thr}",
                args.split))
    else:
        if not has_vb: print("skipped 4way-unanimous-vb: no vitibet_settled data")

    if has_fb and has_betclan_settled:
        sfb = scales["forebet_settled"]
        sbc = scales["betclan_settled"]
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW consensus2_bc AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan_settled)
            SELECT fb.date, fb.outcome,
                   fb.pick AS pick, fb.pick AS fb_pick, bc.pick AS bc_pick,
                   ((fb.pmax/{sfb} + bc.pmax/{sbc})/2)*100 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds
            FROM fb JOIN bc USING (date, hkey, akey)
        """)
        for thr in (60, 65, 70, 75, 80):
            results.append(evaluate(
                con, f"2way-unanimous-bc avg_p>={thr}", "consensus2_bc",
                f"fb_pick = bc_pick AND avg_p >= {thr}", args.split))
    else:
        if not has_betclan_settled: print("skipped 2way-unanimous-bc: no betclan data")
        
    if has_fb and has_bzzoiro_settled:
        sfb = scales["forebet_settled"]
        sbz = scales["bzzoiro_settled"]
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW consensus2_bz AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                 bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro_settled)
            SELECT fb.date, fb.outcome,
                   fb.pick AS pick, fb.pick AS fb_pick, bz.pick AS bz_pick,
                   ((fb.pmax/{sfb} + bz.pmax/{sbz})/2)*100 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds
            FROM fb JOIN bz USING (date, hkey, akey)
        """)
        for thr in (60, 65, 70, 75, 80):
            results.append(evaluate(
                con, f"2way-unanimous-bz avg_p>={thr}", "consensus2_bz",
                f"fb_pick = bz_pick AND avg_p >= {thr}", args.split))
    else:
        if not has_bzzoiro_settled: print("skipped 2way-unanimous-bz: no bzzoiro data")


    # Main consensus views for 1x2 (join the 3 high-volume sources)
    if has_fb and has_zb and has_sa:
        con.execute("""
            CREATE OR REPLACE VIEW consensus3_dense AS
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

    # OU/BTTS consensus (Forebet + Statarea only for maximum volume)
    if has_fb and has_sa:
        sfb, ssa = scales["forebet_settled"], scales["statarea_settled"]
        con.execute(f"""
            CREATE OR REPLACE VIEW consensus_ou_dense AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, 
                               CASE WHEN p_over/{sfb} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou
                        FROM forebet_settled),
                 sa AS (SELECT DISTINCT ON (date, hkey, akey) *, 
                               CASE WHEN p_o25/{ssa} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou
                        FROM statarea_settled)
            SELECT fb.date, fb.home, fb.away,
                   CASE WHEN fb.hs + fb.gs >= 3 THEN 'over' ELSE 'under' END AS outcome,
                   fb.pick_ou AS fb_pick_ou, sa.pick_ou AS sa_pick_ou, fb.pick_ou AS pick,
                   CASE fb.pick_ou WHEN 'over' THEN fb.odd_over ELSE fb.odd_under END AS pick_odds,
                   ((fb.p_over/{sfb} + sa.p_o25/{ssa})/2)*100 AS avg_p
            FROM fb JOIN sa USING (date, hkey, akey)
        """)
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"ou25-unanimous-2way-sa avg_p>={thr}", "consensus_ou_dense",
                f"fb_pick_ou = sa_pick_ou AND avg_p >= {thr}", args.split, market="ou_2.5"))

    # BTTS consensus (Needs BTTS sources - currently FB is the only dense one. 
    # Let's try joining FB with scoutingstats but allow lower overlap for now)
    if has_fb and has_ss:
        sfb, sss = scales["forebet_settled"], scales["scoutingstats_settled"]
        con.execute(f"""
            CREATE OR REPLACE VIEW consensus_btts_sparse AS
            WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, 
                               CASE WHEN p_gg/{sfb} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts
                        FROM forebet_settled),
                 ss AS (SELECT DISTINCT ON (date, hkey, akey) *, 
                               CASE WHEN p_gg/{sss} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts
                        FROM scoutingstats_settled)
            SELECT fb.date,
                   CASE WHEN fb.hs > 0 AND fb.gs > 0 THEN 'yes' ELSE 'no' END AS outcome,
                   fb.pick_btts AS pick,
                   CASE fb.pick_btts WHEN 'yes' THEN fb.odd_gg ELSE fb.odd_ng END AS pick_odds,
                   ((fb.p_gg/{sfb} + ss.p_gg/{sss})/2)*100 AS avg_p
            FROM fb JOIN ss USING (date, hkey, akey)
        """)
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"btts-unanimous-2way-ss avg_p>={thr}", "consensus_btts_sparse",
                f"avg_p >= {thr}", args.split, market="btts", min_n=20))

    hdr = f"{'rule':42s} {'TRAIN n/hit/LB/roi':>26s}   {'VALID n/hit/LB/roi':>26s}  status"
    print(hdr)
    print("-" * len(hdr))
    
    results = [r for r in results if r["train"]["n"] >= GATES.min_overlap_n]
    
    for r in results:
        t, v = r["train"], r["valid"]

        def fmt(s):
            roi = f"{s['roi']:+.1%}" if s["roi"] is not None else "  n/a"
            return f"{s['n']:>6d} {s['hit']:.1%} {s['wilson_lb']:.3f} {roi}"

        flag = "🏆" if r["status"] == "certified" else "  "
        print(f"{r['rule']:42s} {fmt(t):>26s}   {fmt(v):>26s}  {flag} {r['status']}")

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(
        {"split": args.split, "gates": vars(GATES), "edges": results}, indent=2))
    print(f"\nwritten -> {OUT}")


if __name__ == "__main__":
    main()
