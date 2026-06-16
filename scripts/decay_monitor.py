#!/usr/bin/env python3
"""Decay monitor: nightly audit of certified edges (HANDOVER.md golden rule:
HEALTHY / WATCH / DECAYING / DEAD).

    python3 scripts/decay_monitor.py                 # 60-day recent window
    python3 scripts/decay_monitor.py --window 90     # custom window
    python3 scripts/decay_monitor.py --dry-run       # report only, no writes

For every CERTIFIED edge in localdata/edges_consensus.json, re-evaluates the
exact stored rule (`view` + `where`, scales already baked into the where
clause by mine_consensus.py) over the recent window and compares it against
the certified out-of-sample baseline (the edge's `valid` stats) using
edgefactory.assay.decay_verdict / should_bench.

AUTO-BENCH: if should_bench() says so (DEAD / DECAYING, or recent ROI < -5%
with n>=30), the edge's status is flipped to "benched" in the registry.
picks_today.py only uses status=="certified", so benched edges stop being
bet IMMEDIATELY with zero changes to picks code. The next mine_consensus.py
run rebuilds the registry from full data and re-certifies or not — benching
is a circuit breaker, not a permanent verdict.

The registry's `view` names are TEMP views that exist only inside
mine_consensus.py's connection; this script recreates them on top of the
materialized warehouse tables (same SQL contracts). If a view cannot be
rebuilt (e.g. source table missing), that edge is reported UNKNOWN and left
untouched — never crash, never guess.

MUST work with completely empty localdata/: missing warehouse or registry or
zero certified edges -> report and exit 0. Run order: capture -> backfill ->
build_warehouse -> mine_consensus -> decay_monitor -> picks_today.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.assay import decay_verdict, should_bench, wilson_lb  # noqa: E402
from edgefactory.config import GATES  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
REG = ROOT / "localdata" / "edges_consensus.json"


def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def _get_scale(con, view: str) -> float:
    """Same contract as mine_consensus.get_scale: probs >1.5 means 0-100."""
    try:
        max_p = con.sql(f"SELECT max(p1) FROM {view}").fetchone()[0]
        if max_p is not None and float(max_p) > 1.5:
            return 100.0
        return 1.0
    except Exception:
        return 1.0


def recreate_views(con) -> set[str]:
    """Rebuild the TEMP consensus views mine_consensus.py uses, on top of the
    materialized warehouse tables. Returns the set of available view names.
    Every block is independent and failure-tolerant."""
    avail: set[str] = set()
    has = {t: _table_exists(con, t) for t in (
        "forebet_settled", "zulubet_settled", "statarea_settled",
        "vitibet_settled", "scoutingstats_settled", "bettingclosed_settled",
        "betclan", "bzzoiro",
    )}
    scales = {t: (_get_scale(con, t) if has[t] else 1.0) for t in has}

    if has["forebet_settled"] and has["zulubet_settled"] and _table_exists(con, "consensus2"):
        try:
            con.execute("CREATE OR REPLACE TEMP VIEW v_consensus2 AS "
                        "SELECT *, fb_pick AS pick FROM consensus2")
            avail.add("v_consensus2")
        except Exception:
            pass

    if (has["forebet_settled"] and has["zulubet_settled"]
            and has["statarea_settled"] and _table_exists(con, "consensus3")):
        try:
            con.execute("CREATE OR REPLACE TEMP VIEW v_consensus3 AS "
                        "SELECT *, fb_pick AS pick FROM consensus3")
            avail.add("v_consensus3")
        except Exception:
            pass

    if has["betclan"] and has["forebet_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW betclan_settled AS
                WITH bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT bc.*, fb.hs, fb.gs,
                       CASE WHEN bc.p1 >= bc.px AND bc.p1 >= bc.p2 THEN 'home'
                            WHEN bc.p2 >= bc.px THEN 'away' ELSE 'draw' END AS pick,
                       GREATEST(bc.p1, bc.px, bc.p2) AS pmax,
                       CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away'
                            ELSE 'draw' END AS outcome
                FROM bc JOIN fb USING (date, hkey, akey)
            """)
            scales["betclan_settled"] = scales["betclan"]
            avail.add("betclan_settled")
        except Exception:
            pass

    if has["bzzoiro"] and has["forebet_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW bzzoiro_settled AS
                WITH bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey) date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT bz.*, fb.hs, fb.gs,
                       CASE WHEN bz.p1 >= bz.px AND bz.p1 >= bz.p2 THEN 'home'
                            WHEN bz.p2 >= bz.px THEN 'away' ELSE 'draw' END AS pick,
                       GREATEST(bz.p1, bz.px, bz.p2) AS pmax,
                       CASE WHEN fb.hs > fb.gs THEN 'home' WHEN fb.hs < fb.gs THEN 'away'
                            ELSE 'draw' END AS outcome
                FROM bz JOIN fb USING (date, hkey, akey)
            """)
            scales["bzzoiro_settled"] = scales["bzzoiro"]
            avail.add("bzzoiro_settled")
        except Exception:
            pass

    if all(has[t] for t in ("forebet_settled", "zulubet_settled",
                            "statarea_settled", "vitibet_settled")):
        sfb, szb = scales["forebet_settled"], scales["zulubet_settled"]
        ssa, svb = scales["statarea_settled"], scales["vitibet_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus4 AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     zb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM zulubet_settled),
                     sa AS (SELECT DISTINCT ON (date, hkey, akey) * FROM statarea_settled),
                     vb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM vitibet_settled)
                SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, zb.pick AS zb_pick,
                       sa.pick AS sa_pick, vb.pick AS vb_pick,
                       ((fb.pmax/{sfb} + zb.pmax/{szb} + sa.pmax/{ssa} + vb.pmax/{svb})/4)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds,
                       fb.league
                FROM fb JOIN zb USING (date, hkey, akey)
                        JOIN sa USING (date, hkey, akey)
                        JOIN vb USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus4")
        except Exception:
            pass

    if has["forebet_settled"] and "betclan_settled" in avail:
        sfb, sbc = scales["forebet_settled"], scales["betclan_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus2_bc AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     bc AS (SELECT DISTINCT ON (date, hkey, akey) * FROM betclan_settled)
                SELECT fb.date, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, bc.pick AS bc_pick,
                       ((fb.pmax/{sfb} + bc.pmax/{sbc})/2)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds
                FROM fb JOIN bc USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus2_bc")
        except Exception:
            pass

    if has["forebet_settled"] and "bzzoiro_settled" in avail:
        sfb, sbz = scales["forebet_settled"], scales["bzzoiro_settled"]
        try:
            con.execute(f"""
                CREATE OR REPLACE TEMP VIEW consensus2_bz AS
                WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) * FROM forebet_settled),
                     bz AS (SELECT DISTINCT ON (date, hkey, akey) * FROM bzzoiro_settled)
                SELECT fb.date, fb.outcome,
                       fb.pick AS pick, fb.pick AS fb_pick, bz.pick AS bz_pick,
                       ((fb.pmax/{sfb} + bz.pmax/{sbz})/2)*100 AS avg_p,
                       CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx
                            ELSE fb.odd2 END AS pick_odds
                FROM fb JOIN bz USING (date, hkey, akey)
                WHERE length(fb.hkey) >= 4 AND length(fb.akey) >= 4
            """)
            avail.add("consensus2_bz")
        except Exception:
            pass

    # consensus2_bc_confirm: v_consensus2 confirmed by bettingclosed_settled.
    # Joins on (date, home, away) -- consensus2 does not expose hkey/akey.
    if _table_exists(con, "v_consensus2") and has["bettingclosed_settled"]:
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW consensus2_bc_confirm AS
                WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                     bc AS (SELECT DISTINCT ON (date, home, away)
                                   date, home, away,
                                   CASE pick_1x2
                                     WHEN '1' THEN 'home'
                                     WHEN '2' THEN 'away'
                                     WHEN 'x' THEN 'draw'
                                   END AS bc_pick
                            FROM bettingclosed_settled
                            WHERE pick_1x2 IN ('1','2','x'))
                SELECT c2.*, bc.bc_pick
                FROM c2 JOIN bc USING (date, home, away)
            """)
            avail.add("consensus2_bc_confirm")
        except Exception:
            pass



    # Phase A confirmation views: unused 1x2 sources confirming existing
    # consensus rows. Must mirror mine_consensus.py (L1).
    if _table_exists(con, "predictz_settled"):
        try:
            if _table_exists(con, "v_consensus2"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus2_predictz_confirm AS
                    WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                         pz AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, pick AS pz_pick
                                FROM predictz_settled
                                WHERE pick IN ('home','draw','away'))
                    SELECT c2.*, pz.pz_pick
                    FROM c2 JOIN pz USING (date, home, away)
                """)
                avail.add("consensus2_predictz_confirm")
            if _table_exists(con, "v_consensus3"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus3_predictz_confirm AS
                    WITH c3 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus3),
                         pz AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, pick AS pz_pick
                                FROM predictz_settled
                                WHERE pick IN ('home','draw','away'))
                    SELECT c3.*, pz.pz_pick
                    FROM c3 JOIN pz USING (date, home, away)
                """)
                avail.add("consensus3_predictz_confirm")
        except Exception:
            pass

    if _table_exists(con, "windrawwin") and has.get("forebet_settled"):
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW windrawwin_settled AS
                WITH ww AS (SELECT DISTINCT ON (date, hkey, akey) * FROM windrawwin
                            WHERE pick IN ('home','draw','away')),
                     fb AS (SELECT DISTINCT ON (date, hkey, akey)
                                   date, hkey, akey, hs, gs
                            FROM forebet_settled)
                SELECT ww.*, fb.hs, fb.gs,
                       ww.pick AS ww_pick,
                       CASE WHEN fb.hs > fb.gs THEN 'home'
                            WHEN fb.hs < fb.gs THEN 'away' ELSE 'draw' END AS outcome
                FROM ww JOIN fb USING (date, hkey, akey)
            """)
            avail.add("windrawwin_settled")
            if _table_exists(con, "v_consensus2"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus2_windrawwin_confirm AS
                    WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                         ww AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, ww_pick
                                FROM windrawwin_settled)
                    SELECT c2.*, ww.ww_pick
                    FROM c2 JOIN ww USING (date, home, away)
                """)
                avail.add("consensus2_windrawwin_confirm")
            if _table_exists(con, "v_consensus3"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus3_windrawwin_confirm AS
                    WITH c3 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus3),
                         ww AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, ww_pick
                                FROM windrawwin_settled)
                    SELECT c3.*, ww.ww_pick
                    FROM c3 JOIN ww USING (date, home, away)
                """)
                avail.add("consensus3_windrawwin_confirm")
        except Exception:
            pass

    # OU2.5 / BTTS consensus views: source membership depends on what was
    # available at mine time; rebuild with the same membership logic.
    if has["forebet_settled"]:
        sfb = scales["forebet_settled"]
        ou_parts, ou_joins, ou_eq, ou_avg = [], "FROM fb", [], []
        sql = (f"WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, "
               f"CASE WHEN p_over/{sfb} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
               f"FROM forebet_settled)")
        ou_avg.append(f"CASE WHEN fb.pick_ou = 'over' THEN fb.p_over/{sfb} "
                      f"ELSE fb.p_under/{sfb} END")
        n_ou = 1
        if has["statarea_settled"]:
            ssa = scales["statarea_settled"]
            sql += (f", sa AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{ssa} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM statarea_settled)")
            ou_joins += " JOIN sa USING (date, hkey, akey)"
            ou_eq.append("fb.pick_ou = sa.pick_ou")
            ou_avg.append(f"CASE WHEN sa.pick_ou = 'over' THEN sa.p_o25/{ssa} "
                          f"ELSE (1.0 - sa.p_o25/{ssa}) END")
            n_ou += 1
        if has["scoutingstats_settled"]:
            sss = scales["scoutingstats_settled"]
            sql += (f", ss AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{sss} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM scoutingstats_settled)")
            ou_joins += " JOIN ss USING (date, hkey, akey)"
            ou_eq.append("fb.pick_ou = ss.pick_ou")
            ou_avg.append(f"CASE WHEN ss.pick_ou = 'over' THEN ss.p_o25/{sss} "
                          f"ELSE (1.0 - ss.p_o25/{sss}) END")
            n_ou += 1
        if "bzzoiro_settled" in avail:
            sbz = scales["bzzoiro_settled"]
            sql += (f", bz AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_o25/{sbz} >= 0.5 THEN 'over' ELSE 'under' END AS pick_ou "
                    f"FROM bzzoiro_settled)")
            ou_joins += " JOIN bz USING (date, hkey, akey)"
            ou_eq.append("fb.pick_ou = bz.pick_ou")
            ou_avg.append(f"CASE WHEN bz.pick_ou = 'over' THEN bz.p_o25/{sbz} "
                          f"ELSE (1.0 - bz.p_o25/{sbz}) END")
            n_ou += 1
        if n_ou >= 2:
            try:
                con.execute(
                    f"CREATE OR REPLACE TEMP VIEW consensus_ou AS {sql} "
                    f"SELECT fb.date, "
                    f"CASE WHEN fb.hs + fb.gs >= 3 THEN 'over' ELSE 'under' END AS outcome, "
                    f"fb.pick_ou AS fb_pick_ou, fb.pick_ou AS pick, "
                    + ("sa.pick_ou AS sa_pick_ou, " if has["statarea_settled"] else "")
                    + ("ss.pick_ou AS ss_pick_ou, " if has["scoutingstats_settled"] else "")
                    + ("bz.pick_ou AS bz_pick_ou, " if "bzzoiro_settled" in avail else "")
                    + f"CASE fb.pick_ou WHEN 'over' THEN fb.odd_over ELSE fb.odd_under END AS pick_odds, "
                    f"(({'+'.join(ou_avg)})/{len(ou_avg)})*100 AS avg_p {ou_joins}"
                )
                avail.add("consensus_ou")
            except Exception:
                pass

        btts_avg, btts_joins, n_btts = [], "FROM fb", 1
        sql = (f"WITH fb AS (SELECT DISTINCT ON (date, hkey, akey) *, "
               f"CASE WHEN p_gg/{sfb} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
               f"FROM forebet_settled)")
        btts_avg.append(f"CASE WHEN fb.pick_btts = 'yes' THEN fb.p_gg/{sfb} "
                        f"ELSE fb.p_ng/{sfb} END")
        if has["scoutingstats_settled"]:
            sss = scales["scoutingstats_settled"]
            sql += (f", ss AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_gg/{sss} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
                    f"FROM scoutingstats_settled)")
            btts_joins += " JOIN ss USING (date, hkey, akey)"
            btts_avg.append(f"CASE WHEN ss.pick_btts = 'yes' THEN ss.p_gg/{sss} "
                            f"ELSE (1.0 - ss.p_gg/{sss}) END")
            n_btts += 1
        if "bzzoiro_settled" in avail:
            sbz = scales["bzzoiro_settled"]
            sql += (f", bz AS (SELECT DISTINCT ON (date, hkey, akey) *, "
                    f"CASE WHEN p_gg/{sbz} >= 0.5 THEN 'yes' ELSE 'no' END AS pick_btts "
                    f"FROM bzzoiro_settled)")
            btts_joins += " JOIN bz USING (date, hkey, akey)"
            btts_avg.append(f"CASE WHEN bz.pick_btts = 'yes' THEN bz.p_gg/{sbz} "
                            f"ELSE (1.0 - bz.p_gg/{sbz}) END")
            n_btts += 1
        if n_btts >= 2:
            try:
                con.execute(
                    f"CREATE OR REPLACE TEMP VIEW consensus_btts AS {sql} "
                    f"SELECT fb.date, "
                    f"CASE WHEN fb.hs > 0 AND fb.gs > 0 THEN 'yes' ELSE 'no' END AS outcome, "
                    f"fb.pick_btts AS fb_pick_btts, fb.pick_btts AS pick, "
                    + ("ss.pick_btts AS ss_pick_btts, " if has["scoutingstats_settled"] else "")
                    + ("bz.pick_btts AS bz_pick_btts, " if "bzzoiro_settled" in avail else "")
                    + f"CASE fb.pick_btts WHEN 'yes' THEN fb.odd_gg ELSE fb.odd_ng END AS pick_odds, "
                    f"(({'+'.join(btts_avg)})/{len(btts_avg)})*100 AS avg_p {btts_joins}"
                )
                avail.add("consensus_btts")
            except Exception:
                pass

    return avail


def recent_stats(con, view: str, where: str, since: str):
    """Same accounting as mine_consensus.stats(), restricted to date >= since."""
    q = f"""
        SELECT count(*) n,
               sum(CASE WHEN pick = outcome THEN 1 ELSE 0 END) wins,
               sum(CASE WHEN pick_odds IS NOT NULL THEN
                     CASE WHEN pick = outcome THEN pick_odds - 1 ELSE -1 END
                   ELSE 0 END) pnl,
               sum(CASE WHEN pick_odds IS NOT NULL THEN 1 ELSE 0 END) n_priced
        FROM {view} WHERE ({where}) AND date >= '{since}'
    """
    n, wins, pnl, n_priced = con.sql(q).fetchone()
    n, wins, n_priced = int(n or 0), int(wins or 0), int(n_priced or 0)
    return {
        "n": n, "wins": wins,
        "hit": round(wins / n, 4) if n else 0.0,
        "wilson_lb": round(wilson_lb(wins, n), 4),
        "roi": round(pnl / n_priced, 4) if n_priced else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=GATES.recent_window_days,
                    help="recent window in days (default from config)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report only, do not update the registry")
    args = ap.parse_args()

    if not REG.exists():
        print("No edges_consensus.json — nothing to audit. "
              "Run mine_consensus.py first. Exit 0.")
        return
    try:
        reg = json.loads(REG.read_text())
        edges = reg.get("edges", [])
    except (json.JSONDecodeError, AttributeError) as e:
        print(f"Registry unreadable ({e}) — nothing to audit. Exit 0.")
        return

    certified = [e for e in edges if e.get("status") == "certified"]
    benched_already = [e for e in edges if e.get("status") == "benched"]
    if not certified:
        print(f"0 certified edges in registry "
              f"({len(benched_already)} already benched). Nothing to audit. Exit 0.")
        return

    if not DB.exists():
        print(f"{len(certified)} certified edges but no warehouse — "
              "cannot audit, registry left untouched. "
              "Run build_warehouse.py first. Exit 0.")
        return

    import duckdb
    con = duckdb.connect(str(DB), read_only=True)
    avail = recreate_views(con)
    since = (date.today() - timedelta(days=args.window)).isoformat()
    today = date.today().isoformat()

    hdr = (f"{'rule':42s} {'market':7s} {'baseline n/hit/LB':>20s} "
           f"{'recent n/hit/LB/roi':>24s}  verdict")
    print(f"Decay audit {today}, window {args.window}d (since {since})")
    print(hdr)
    print("-" * len(hdr))

    n_benched = 0
    for e in certified:
        rule, market = e.get("rule", "?"), e.get("market", "1x2")
        view, where = e.get("view"), e.get("where")
        base = e.get("valid") or {}
        b_wins, b_n = int(base.get("wins") or 0), int(base.get("n") or 0)

        if not view or not where or view not in avail or not b_n:
            e["decay"] = {"verdict": "UNKNOWN", "window_days": args.window,
                          "checked_at": today,
                          "reason": "view unavailable or baseline missing"}
            print(f"{rule:42s} {market:7s} {'?':>20s} {'?':>24s}  UNKNOWN (skipped)")
            continue

        try:
            rec = recent_stats(con, view, where, since)
        except Exception as ex:
            e["decay"] = {"verdict": "UNKNOWN", "window_days": args.window,
                          "checked_at": today, "reason": str(ex)[:120]}
            print(f"{rule:42s} {market:7s} {'?':>20s} {'?':>24s}  UNKNOWN (query failed)")
            continue

        rep = decay_verdict(b_wins, b_n, rec["wins"], rec["n"],
                            min_recent=GATES.min_recent_n)
        bench = should_bench(rep, rec["roi"])
        e["decay"] = {
            "verdict": rep.verdict, "window_days": args.window,
            "checked_at": today, "recent": rec,
            "baseline_lb": round(rep.baseline_lb, 4),
            "recent_lb": round(rep.recent_lb, 4),
            "recent_ub": round(rep.recent_ub, 4),
        }
        if bench:
            e["status"] = "benched"
            e["benched_at"] = today
            n_benched += 1

        b_str = f"{b_n:>5d} {base.get('hit', 0):.1%} {base.get('wilson_lb', 0):.3f}"
        roi_s = f"{rec['roi']:+.1%}" if rec["roi"] is not None else "  n/a"
        r_str = f"{rec['n']:>5d} {rec['hit']:.1%} {rec['wilson_lb']:.3f} {roi_s}"
        flag = " -> BENCHED" if bench else ""
        print(f"{rule:42s} {market:7s} {b_str:>20s} {r_str:>24s}  {rep.verdict}{flag}")

    print(f"\n{len(certified)} certified audited, {n_benched} benched this run, "
          f"{len(benched_already)} previously benched.")
    if n_benched:
        print("Benched edges are OUT of picks_today immediately "
              "(it only reads status=='certified').")
        print("Next mine_consensus.py run re-certifies from scratch on the full "
              "walk-forward history — benching is a 60-day-window circuit breaker, "
              "not a permanent verdict.")

    if args.dry_run:
        print("--dry-run: registry NOT updated.")
        return
    REG.write_text(json.dumps(reg, indent=2))
    print(f"registry updated -> {REG}")


if __name__ == "__main__":
    main()
