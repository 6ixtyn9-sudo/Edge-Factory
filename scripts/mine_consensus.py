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
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb  # noqa: E402

from edgefactory.assay import wilson_lb, weighted_consensus_score  # noqa: E402
from edgefactory.entities import classify_competition  # noqa: E402
from edgefactory.config import GATES  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
OUT = ROOT / "localdata" / "edges_consensus.json"


def _count_certified(edges: list[dict]) -> int:
    return sum(1 for e in edges if e.get("status") == "certified")


def _existing_certified_count() -> int:
    """Count certified edges already present in OUT, or 0 if missing/invalid."""
    if not OUT.exists():
        return 0
    try:
        data = json.loads(OUT.read_text())
        return _count_certified(data.get("edges", []))
    except Exception:
        return 0


def write_registry(payload: dict) -> bool:
    """Persist the mined registry with a regression-to-zero circuit breaker.

    Deep walk-forward history (pre-split training rows) lives only on the
    operator's local machine and in the GitHub Actions cache. On a cold or
    evicted cache the warehouse holds only a rolling D30 window, which is
    entirely post-split, so no rule can satisfy min_n_train and the miner
    yields 0 certified edges.

    Left unguarded, that empty result overwrites a good registry and cascades
    into empty picks, empty WhatsApps, and a frozen intraday loop. This guard
    preserves the last known-good registry whenever a run certifies nothing but
    the existing file already holds certified edges.

    Returns True if a new file was written, False if the existing file was kept.
    """
    new_certified = _count_certified(payload.get("edges", []))
    existing_certified = _existing_certified_count()

    if new_certified == 0 and existing_certified > 0:
        print(
            "\n⚠️  REGRESSION GUARD: this run certified 0 edges, but the existing "
            f"registry already holds {existing_certified} certified edge(s)."
        )
        print("    Keeping the existing registry to avoid clobbering certified edges.")
        print("    Usual cause: cold/evicted warehouse missing pre-split training history")
        print("    (capture_daily only backfills a D30 window, all of it post-split).")
        print("    Restore: re-run on a machine with full history, or commit edges_consensus.json")
        print("    into the repo so the certified registry survives cache loss (see HANDOVER.md).")
        print(f"    Preserved file: {OUT}")
        return False

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"\nwritten -> {OUT}  (certified={new_certified})")
    return True


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
            "sport": "soccer",
            "train": tr, "valid": va,
            "status": "certified" if certified else "candidate"}


def _edge_preference(edge: dict) -> tuple[int, int, int]:
    """Higher is better when two certified edges have identical realized stats.

    This keeps the more general/canonical rule when a stricter description adds
    no rows or performance difference, e.g. `2way-unanimous avg_p>=70` vs
    `2way-unanimous no-draw avg_p>=70` when the threshold already removes draws.
    """
    rule = edge.get("rule", "").lower()
    return (
        0 if "no-draw" in rule else 1,
        0 if "veto-check" in rule else 1,
        -len(rule),
    )


def _equivalence_signature(edge: dict) -> tuple | None:
    """Signature for certified-edge de-duplication.

    Only certified edges are collapsed, and only when the same view/market has
    exactly the same walk-forward accounting. Candidate scans remain visible.
    """
    if edge.get("status") != "certified":
        return None
    return (
        edge.get("sport", "soccer"),
        edge.get("market", "1x2"),
        edge.get("view"),
        json.dumps(edge.get("train", {}), sort_keys=True),
        json.dumps(edge.get("valid", {}), sort_keys=True),
    )


def dedupe_equivalent_certified_edges(results: list[dict]) -> tuple[list[dict], list[dict]]:
    """Remove duplicate certified edges with identical realized train/valid stats.

    Returns (deduped_results, removed_edges). Order is stable except when a later
    canonical rule replaces an earlier duplicate with the same signature.
    """
    out: list[dict] = []
    sig_to_pos: dict[tuple, int] = {}
    removed: list[dict] = []
    for edge in results:
        sig = _equivalence_signature(edge)
        if sig is None:
            out.append(edge)
            continue
        if sig not in sig_to_pos:
            sig_to_pos[sig] = len(out)
            out.append(edge)
            continue
        pos = sig_to_pos[sig]
        incumbent = out[pos]
        if _edge_preference(edge) > _edge_preference(incumbent):
            removed.append(incumbent)
            out[pos] = edge
        else:
            removed.append(edge)
    return out, removed


def _source_wilson_lbs(con, split: str) -> dict[str, dict[str, float]]:
    """Compute Wilson LB for each source on each market using the TRAINING period.

    Returns a nested dict:  source_name -> market -> wilson_lb
    Only includes sources/markets with >= GATES.min_n_train rows in training.

    The LB is measured on the source's own picks (no cross-joining).  This is
    used as the per-source vote weight in weighted consensus mining.
    """
    # (view_name, source_key, market, pick_col, outcome_col, scale_divisor)
    SINGLE_SOURCE_SPECS = []

    for view, key, mkt in [
        ("forebet_settled",    "forebet",    "1x2"),
        ("zulubet_settled",    "zulubet",    "1x2"),
        ("statarea_settled",   "statarea",   "1x2"),
        ("vitibet_settled",    "vitibet",    "1x2"),
        ("scoutingstats_settled", "scoutingstats", "1x2"),
    ]:
        if _table_exists(con, view):
            SINGLE_SOURCE_SPECS.append((view, key, mkt, "pick", "outcome", 1.0))

    # OU 2.5
    if _table_exists(con, "forebet_settled"):
        SINGLE_SOURCE_SPECS.append(("forebet_settled", "forebet", "ou_2.5",
                                    "CASE WHEN p_over/1.0 >= 0.5 THEN 'over' ELSE 'under' END",
                                    "CASE WHEN hs+gs >= 3 THEN 'over' ELSE 'under' END", 1.0))
    if _table_exists(con, "statarea_settled"):
        SINGLE_SOURCE_SPECS.append(("statarea_settled", "statarea", "ou_2.5",
                                    "CASE WHEN p_o25/1.0 >= 0.5 THEN 'over' ELSE 'under' END",
                                    "CASE WHEN hs+gs >= 3 THEN 'over' ELSE 'under' END", 1.0))
    if _table_exists(con, "scoutingstats_settled"):
        SINGLE_SOURCE_SPECS.append(("scoutingstats_settled", "scoutingstats", "ou_2.5",
                                    "CASE WHEN p_o25/1.0 >= 0.5 THEN 'over' ELSE 'under' END",
                                    "CASE WHEN hs+gs >= 3 THEN 'over' ELSE 'under' END", 1.0))

    # BTTS
    if _table_exists(con, "forebet_settled"):
        SINGLE_SOURCE_SPECS.append(("forebet_settled", "forebet", "btts",
                                    "CASE WHEN p_gg/1.0 >= 0.5 THEN 'yes' ELSE 'no' END",
                                    "CASE WHEN hs > 0 AND gs > 0 THEN 'yes' ELSE 'no' END", 1.0))
    if _table_exists(con, "scoutingstats_settled"):
        SINGLE_SOURCE_SPECS.append(("scoutingstats_settled", "scoutingstats", "btts",
                                    "CASE WHEN p_gg/1.0 >= 0.5 THEN 'yes' ELSE 'no' END",
                                    "CASE WHEN hs > 0 AND gs > 0 THEN 'yes' ELSE 'no' END", 1.0))

    out: dict[str, dict[str, float]] = {}

    for view, key, mkt, pick_expr, outcome_expr, _ in SINGLE_SOURCE_SPECS:
        try:
            row = con.execute(f"""
                SELECT count(*) AS n,
                       sum(CASE WHEN ({pick_expr}) = ({outcome_expr}) THEN 1 ELSE 0 END) AS wins
                FROM {view}
                WHERE date < '{split}'
                  AND hs IS NOT NULL AND gs IS NOT NULL
            """).fetchone()
            n, wins = int(row[0] or 0), int(row[1] or 0)
            if n >= GATES.min_n_train:
                lb = wilson_lb(wins, n)
                out.setdefault(key, {})[mkt] = round(lb, 4)
        except Exception:
            pass

    return out


# Source weight table used in pick-time weighted consensus (also exported via
# mine so that picks_today.py can read it from edges_consensus.json).
_WEIGHTED_SOURCES_1X2   = ["forebet", "zulubet", "statarea", "vitibet", "scoutingstats"]
_WEIGHTED_SOURCES_OU25  = ["forebet", "statarea", "scoutingstats"]
_WEIGHTED_SOURCES_BTTS  = ["forebet", "scoutingstats"]


def _run_weighted_consensus(con, split: str, source_lbs: dict[str, dict[str, float]],
                             results: list[dict], scales: dict[str, float]) -> None:
    """Mine weighted consensus rules and append to results."""
    avail_1x2 = [s for s in _WEIGHTED_SOURCES_1X2 if s in source_lbs
                 and "1x2" in source_lbs[s]]
    if len(avail_1x2) >= 2:
        unions = []
        for src in avail_1x2:
            view = f"{src}_settled"
            if not _table_exists(con, view):
                continue
            scale = scales.get(view, 1.0)
            unions.append(f"""
                SELECT date, hkey, akey, home, away, outcome, league,
                       pick, pmax/{scale} AS prob,
                       CASE pick WHEN 'home' THEN odd1 WHEN 'draw' THEN oddx ELSE odd2 END AS pick_odds,
                       '{src}' AS source
                FROM (SELECT DISTINCT ON (date, hkey, akey) * FROM {view})
            """)
        if len(unions) >= 2:
            unioned = " UNION ALL ".join(unions)
            try:
                rows = con.execute(f"""
                    WITH base AS ({unioned})
                    SELECT date, hkey, akey, home, away, outcome, league,
                           source, pick, prob, pick_odds,
                           MIN(pick_odds) FILTER (WHERE pick_odds IS NOT NULL) OVER
                               (PARTITION BY date, hkey, akey) AS best_pick_odds
                    FROM base
                    WHERE outcome IS NOT NULL
                    ORDER BY date, hkey, akey, source
                """).fetchall()
            except Exception:
                try:
                    rows = con.execute(f"""
                        WITH base AS ({unioned})
                        SELECT date, hkey, akey, home, away, outcome, league,
                               source, pick, prob, pick_odds, pick_odds AS best_pick_odds
                        FROM base
                        ORDER BY date, hkey, akey, source
                    """).fetchall()
                except Exception:
                    rows = []

            matches: dict[tuple, dict] = {}
            for date_, hkey, akey, home, away, outcome, league, source, pick, prob, pick_odds, best_odds in rows:
                key = (date_, hkey, akey)
                if key not in matches:
                    matches[key] = {
                        "date": date_, "home": home, "away": away,
                        "outcome": outcome, "league": league,
                        "pick_odds": None, "votes": []
                    }
                if best_odds is not None and matches[key]["pick_odds"] is None:
                    matches[key]["pick_odds"] = best_odds
                if source in avail_1x2:
                    lb = source_lbs[source]["1x2"]
                    matches[key]["votes"].append((pick, lb))

            for w_thr in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80):
                rule_name = f"weighted-1x2 w_score>={w_thr:.2f}"
                qualifying: list[dict] = []
                for match in matches.values():
                    winning_pick, w_score, is_unanimous = weighted_consensus_score(match["votes"])
                    if not is_unanimous:
                        continue
                    if w_score < w_thr:
                        continue
                    qualifying.append({
                        "date": match["date"],
                        "pick": winning_pick,
                        "outcome": match["outcome"],
                        "pick_odds": match["pick_odds"],
                        "w_score": w_score,
                    })

                def _stats_from_list(rows_list: list[dict], split_: str, period: str) -> dict:
                    subset = [r for r in rows_list
                              if (r["date"] < split_) == (period == "train")]
                    n = len(subset)
                    wins_ = sum(1 for r in subset if r["pick"] == r["outcome"])
                    priced = [r for r in subset if r["pick_odds"] is not None]
                    pnl = sum((r["pick_odds"] - 1) if r["pick"] == r["outcome"] else -1
                              for r in priced)
                    roi_ = pnl / len(priced) if priced else None
                    return {
                        "n": n, "wins": wins_,
                        "hit": round(wins_ / n, 4) if n else 0.0,
                        "wilson_lb": round(wilson_lb(wins_, n), 4),
                        "avg_odds": None, "roi": round(roi_, 4) if roi_ is not None else None,
                        "n_priced": len(priced),
                    }

                tr = _stats_from_list(qualifying, split, "train")
                va = _stats_from_list(qualifying, split, "valid")
                if tr["n"] < GATES.min_overlap_n:
                    continue
                certified = (
                    tr["n"] >= GATES.min_n_train
                    and va["n"] >= GATES.min_n_valid
                    and (tr["roi"] is None or tr["roi"] >= GATES.min_roi_train)
                    and (va["roi"] is None or va["roi"] >= GATES.min_roi_valid)
                    and va["wilson_lb"] >= 0.5
                )
                results.append({
                    "rule": rule_name,
                    "view": "weighted_1x2",
                    "where": f"w_score >= {w_thr}",
                    "market": "1x2",
                    "sport": "soccer",
                    "weighted": True,
                    "source_weights": {s: source_lbs[s]["1x2"] for s in avail_1x2},
                    "sources": avail_1x2,
                    "train": tr, "valid": va,
                    "status": "certified" if certified else "candidate",
                })


# ---- Machine Learning Meta-Classifier (The Level-2 Miner) ----------------

def train_ml_meta_classifier(con, split: str) -> tuple[dict, LogisticRegression] | tuple[None, None]:
    """Train walking-forward Logistic Regression model on consensus3.

    Saves weights/intercepts inside the edges_consensus.json registry itself.
    """
    if not _table_exists(con, "consensus3"):
        return None, None

    q = """
        SELECT date, home, away, outcome, league,
               fb_pick, zb_pick, sa_pick,
               fb_p, zb_p, sa_p,
               pick_odds
        FROM consensus3
        WHERE outcome IS NOT NULL AND fb_p IS NOT NULL AND zb_p IS NOT NULL AND sa_p IS NOT NULL
        ORDER BY date
    """
    try:
        df = con.execute(q).df()
    except Exception as exc:
        print(f"ML Meta training skipped (failed query): {exc}")
        return None, None

    if len(df) < 500:
        print(f"ML Meta training skipped (insufficient rows: {len(df)} < 500)")
        return None, None

    def get_majority_pick(row):
        p1, p2, p3 = row['fb_pick'], row['zb_pick'], row['sa_pick']
        if p1 == p2 or p1 == p3:
            return p1
        if p2 == p3:
            return p2
        return p1

    df['pick'] = df.apply(get_majority_pick, axis=1)
    df['y'] = (df['pick'] == df['outcome']).astype(int)

    probs = df[['fb_p', 'zb_p', 'sa_p']].values
    df['avg_p'] = np.mean(probs, axis=1)
    df['min_p'] = np.min(probs, axis=1)
    df['std_p'] = np.std(probs, axis=1)

    df['is_home'] = (df['pick'] == 'home').astype(int)
    df['is_away'] = (df['pick'] == 'away').astype(int)

    df['cat'] = df['league'].apply(classify_competition)
    for cat in ['friendly', 'youth', 'women', 'cup', 'league']:
        df[f'cat_{cat}'] = (df['cat'] == cat).astype(int)

    df['date_dt'] = pd.to_datetime(df['date'])
    daily = df.groupby('date_dt').agg(wins=('y', 'sum'), total=('y', 'count')).reset_index()
    daily = daily.sort_values('date_dt')
    daily['shift_wins'] = daily['wins'].shift(1)
    daily['shift_total'] = daily['total'].shift(1)
    daily['rolling_wins'] = daily.rolling('14D', on='date_dt')['shift_wins'].sum()
    daily['rolling_total'] = daily.rolling('14D', on='date_dt')['shift_total'].sum()
    daily['rolling_hit_rate'] = daily['rolling_wins'] / daily['rolling_total']
    daily['rolling_hit_rate'] = daily['rolling_hit_rate'].fillna(0.75)

    df = df.merge(daily[['date_dt', 'rolling_hit_rate']], on='date_dt', how='left')
    df['pick_odds'] = pd.to_numeric(df['pick_odds'], errors='coerce').fillna(1.50)

    feature_cols = [
        'fb_p', 'zb_p', 'sa_p',
        'avg_p', 'min_p', 'std_p',
        'pick_odds',
        'is_home', 'is_away',
        'cat_friendly', 'cat_youth', 'cat_women', 'cat_cup', 'cat_league',
        'rolling_hit_rate'
    ]

    train_df = df[df['date'] < split]
    if len(train_df) < 300:
        print(f"ML Meta training skipped (insufficient train size: {len(train_df)} < 300)")
        return None, None

    X_train = train_df[feature_cols].values
    y_train = train_df['y'].values

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train, y_train)

    # Generate probabilities for ALL matches
    df['ml_p'] = model.predict_proba(df[feature_cols].values)[:, 1]

    # Register in DuckDB view
    con.register('ml_meta_raw_df', df[['date', 'home', 'away', 'ml_p', 'pick']])
    con.execute("""
        CREATE OR REPLACE TEMP VIEW ml_meta_settled AS
        WITH ml AS (SELECT DISTINCT ON (date, home, away) * FROM ml_meta_raw_df),
             c3 AS (SELECT DISTINCT ON (date, home, away) * FROM consensus3)
        SELECT c3.sport, c3.date, c3.home, c3.away, c3.outcome,
               ml.pick, ml.ml_p, c3.pick_odds, c3.league
        FROM c3 JOIN ml USING (date, home, away)
    """)

    payload = {
        "coef": list(model.coef_[0]),
        "intercept": float(model.intercept_[0]),
        "feature_cols": feature_cols,
    }
    
    # Save predictions to disk so subsequent pipeline stages can recreate the view natively
    try:
        ML_PREDS_PATH = ROOT / "localdata" / "ml_meta_predictions.csv.gz"
        df[['date', 'home', 'away', 'ml_p', 'pick']].to_csv(ML_PREDS_PATH, index=False, compression="gzip")
        print(f"Saved {len(df):,} ML predictions to disk -> {ML_PREDS_PATH}")
    except Exception as exc:
        print(f"Failed to save ML predictions to disk: {exc}")

    print(f"ML Meta-Classifier trained successfully! coefficients={payload['coef']}, intercept={payload['intercept']}")
    return payload, model


def create_phase_a_confirmation_views(con) -> set[str]:
    """Create Phase A unused-source confirmation views."""
    made: set[str] = set()

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
                made.add("consensus2_predictz_confirm")
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
                made.add("consensus3_predictz_confirm")
        except Exception as exc:
            print(f"skipped predictz confirmation views: {exc}")

    if _table_exists(con, "windrawwin") and _table_exists(con, "forebet_settled"):
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
            made.add("windrawwin_settled")
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
                made.add("consensus2_windrawwin_confirm")
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
                made.add("consensus3_windrawwin_confirm")
        except Exception as exc:
            print(f"skipped windrawwin confirmation views: {exc}")

    return made


def run_phase_a_confirmation_levers(con, results: list[dict], split: str,
                                    scales: dict[str, float]) -> None:
    """Mine Phase A additive confirmation levers for unused 1x2 sources."""
    made = create_phase_a_confirmation_views(con)
    sfb = scales.get("forebet_settled", 1.0)
    szb = scales.get("zulubet_settled", 1.0)
    ssa = scales.get("statarea_settled", 1.0)

    if "consensus2_predictz_confirm" in made:
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"2way+predictz-confirms avg_p>={thr}", "consensus2_predictz_confirm",
                f"fb_pick = zb_pick AND fb_pick = pz_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                split,
            ))
    else:
        if not _table_exists(con, "predictz_settled"):
            print("skipped predictz confirmation: no predictz_settled data")

    if "consensus3_predictz_confirm" in made:
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way+predictz-confirms avg_p>={thr}", "consensus3_predictz_confirm",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND fb_pick = pz_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                split,
            ))

    if "consensus2_windrawwin_confirm" in made:
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"2way+windrawwin-confirms avg_p>={thr}", "consensus2_windrawwin_confirm",
                f"fb_pick = zb_pick AND fb_pick = ww_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                split,
            ))
    else:
        if not _table_exists(con, "windrawwin"):
            print("skipped windrawwin confirmation: no windrawwin data")

    if "consensus3_windrawwin_confirm" in made:
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way+windrawwin-confirms avg_p>={thr}", "consensus3_windrawwin_confirm",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND fb_pick = ww_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                split,
            ))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default=GATES.walkforward_split)
    args = ap.parse_args()

    if not DB.exists():
        print("Warehouse does not exist, exiting gracefully.")
        write_registry({"split": args.split, "gates": vars(GATES), "edges": []})
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

    # ---- Train and Evaluate ML Meta-Classifier -----------------------------
    ml_model_payload, _ = train_ml_meta_classifier(con, args.split)
    if ml_model_payload:
        for thr in (70, 75, 80, 85):
            results.append(evaluate(
                con, f"ml-meta avg_p>={thr}", "ml_meta_settled",
                f"ml_p*100 >= {thr}", args.split))

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

    # ---- Accuracy levers ---------------------------------------------------
    if has_fb and has_zb and has_sa:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way-unanimous no-draw avg_p>={thr}", "v_consensus3",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND fb_pick != 'draw' "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                args.split))

    if has_fb and has_zb:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        for thr in (65, 70, 75):
            results.append(evaluate(
                con, f"2way-unanimous min_p>=60 avg_p>={thr}", "v_consensus2",
                f"fb_pick = zb_pick "
                f"AND fb_p/{sfb} >= 0.60 AND zb_p/{szb} >= 0.60 "
                f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                args.split))
    if has_fb and has_zb and has_sa:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way-unanimous min_p>=60 avg_p>={thr}", "v_consensus3",
                f"fb_pick = zb_pick AND zb_pick = sa_pick "
                f"AND fb_p/{sfb} >= 0.60 AND zb_p/{szb} >= 0.60 AND sa_p/{ssa} >= 0.60 "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                args.split))

    if has_fb and has_zb:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        for thr in (65, 70, 75):
            results.append(evaluate(
                con, f"2way-unanimous odds-1.20-1.75 avg_p>={thr}", "v_consensus2",
                f"fb_pick = zb_pick "
                f"AND pick_odds >= 1.20 AND pick_odds < 1.75 "
                f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                args.split))
    if has_fb and has_zb and has_sa:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way-unanimous odds-1.20-1.75 avg_p>={thr}", "v_consensus3",
                f"fb_pick = zb_pick AND zb_pick = sa_pick "
                f"AND pick_odds >= 1.20 AND pick_odds < 1.75 "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                args.split))

    if has_fb and has_zb:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        for sel in ("home", "away"):
            for thr in (65, 70):
                results.append(evaluate(
                    con, f"2way-unanimous {sel}-only avg_p>={thr}", "v_consensus2",
                    f"fb_pick = zb_pick AND fb_pick = '{sel}' "
                    f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                    args.split))
    if has_fb and has_zb and has_sa:
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
        ssa = scales["statarea_settled"]
        for sel in ("home", "away"):
            for thr in (60, 65):
                results.append(evaluate(
                    con, f"3way-unanimous {sel}-only avg_p>={thr}", "v_consensus3",
                    f"fb_pick = zb_pick AND zb_pick = sa_pick AND fb_pick = '{sel}' "
                    f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                    args.split))

    has_bc_settled_full = _table_exists(con, "bettingclosed_settled")
    if has_fb and has_zb and has_bc_settled_full and _table_exists(con, "v_consensus2"):
        sfb = scales["forebet_settled"]
        szb = scales["zulubet_settled"]
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
                SELECT c2.*,
                       bc.bc_pick
                FROM c2 JOIN bc USING (date, home, away)
            """)
            for thr in (60, 65, 70, 75):
                results.append(evaluate(
                    con, f"2way+bc-confirms avg_p>={thr}", "consensus2_bc_confirm",
                    f"fb_pick = zb_pick AND fb_pick = bc_pick "
                    f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                    args.split))
        except Exception as exc:
            print(f"skipped 2way+bc-confirms: {exc}")
    else:
        if not has_bc_settled_full:
            print("skipped 2way+bc-confirms: no bettingclosed_settled data")

    run_phase_a_confirmation_levers(con, results, args.split, scales)

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
            SELECT fb.sport, fb.date, fb.home, fb.away, fb.outcome,
                   fb.pick AS pick, fb.pick AS fb_pick, zb.pick AS zb_pick, sa.pick AS sa_pick, vb.pick AS vb_pick,
                   ((fb.pmax/{sfb} + zb.pmax/{szb} + sa.pmax/{ssa} + vb.pmax/{svb})/4)*100 AS avg_p,
                   CASE fb.pick WHEN 'home' THEN fb.odd1 WHEN 'draw' THEN fb.oddx ELSE fb.odd2 END AS pick_odds,
                   fb.league
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

    if has_fb and has_zb and has_sa:
        con.execute("""
            CREATE OR REPLACE TEMP VIEW consensus3_dense AS
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

    if has_fb and has_sa:
        sfb, ssa = scales["forebet_settled"], scales["statarea_settled"]
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW consensus_ou_dense AS
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

    if has_fb and has_ss:
        sfb, sss = scales["forebet_settled"], scales["scoutingstats_settled"]
        con.execute(f"""
            CREATE OR REPLACE TEMP VIEW consensus_btts_sparse AS
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
                f"avg_p >= {thr}", args.split, market="btts"))

    source_lbs = _source_wilson_lbs(con, args.split)
    if source_lbs:
        print(f"\nSource Wilson LBs for weighting (training period < {args.split}):")
        for src, mkts in sorted(source_lbs.items()):
            for mkt, lb in sorted(mkts.items()):
                print(f"  {src:20s} {mkt:8s}  LB={lb:.4f}")
        _run_weighted_consensus(con, args.split, source_lbs, results, scales)
    else:
        print("Weighted consensus skipped: insufficient per-source training data.")

    def fmt_stats(s):
        roi = f"{s['roi']:+.1%}" if s["roi"] is not None else "  n/a"
        return f"{s['n']:>6d} {s['hit']:.1%} {s['wilson_lb']:.3f} {roi}"

    phase_a_shadow = [
        r for r in results
        if ("predictz-confirms" in r.get("rule", "") or "windrawwin-confirms" in r.get("rule", ""))
        and r["train"]["n"] < GATES.min_overlap_n
    ]
    if phase_a_shadow:
        print("\nPhase A shadow confirmation levers — evaluated but excluded from registry")
        print(f"Reason: train n < min_overlap_n ({GATES.min_overlap_n}); capture-forward sources have no pre-split training yet.")
        shdr = f"{'rule':48s} {'TRAIN n/hit/LB/roi':>26s}   {'VALID n/hit/LB/roi':>26s}  status"
        print(shdr)
        print("-" * len(shdr))
        for r in phase_a_shadow:
            print(f"{r['rule']:48s} {fmt_stats(r['train']):>26s}   {fmt_stats(r['valid']):>26s}  shadow")

    hdr = f"{'rule':48s} {'TRAIN n/hit/LB/roi':>26s}   {'VALID n/hit/LB/roi':>26s}  status"
    print(hdr)
    print("-" * len(hdr))
    
    results = [r for r in results if r["train"]["n"] >= GATES.min_overlap_n]
    results, deduped = dedupe_equivalent_certified_edges(results)
    if deduped:
        print(f"de-duped {len(deduped)} equivalent certified edge(s)")
    
    for r in results:
        t, v = r["train"], r["valid"]
        flag = "🏆" if r["status"] == "certified" else "  "
        wtag = " [W]" if r.get("weighted") else ""
        print(f"{r['rule']:48s} {fmt_stats(t):>26s}   {fmt_stats(v):>26s}  {flag} {r['status']}{wtag}")

    payload = {"split": args.split, "gates": vars(GATES), "edges": results}
    if ml_model_payload:
        payload["ml_model"] = ml_model_payload

    write_registry(payload)


if __name__ == "__main__":
    main()
