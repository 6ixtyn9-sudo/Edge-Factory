#!/usr/bin/env python3
"""Walk-forward re-mining of retained non-Forebet sources and markets.

The existing daily entry point now scans explicit current electorates, singles,
unanimity, strict-majority and disagreement-follow strategies. It writes the
existing research report; it cannot activate new predicates without serving
validation. Legacy helpers remain for frozen model protection and historical
receipts, not as the current default mining electorate.

    python3 scripts/mine_consensus.py --as-of 2026-10-19 --split 2026-09-21
"""
from __future__ import annotations

import argparse
import json
import os
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from itertools import combinations
import subprocess
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import duckdb  # noqa: E402

from edgefactory.assay import wilson_lb, weighted_consensus_score  # noqa: E402
from edgefactory.identity import source_team_key
from edgefactory.market_registry import get_bettable_markets
from edgefactory.entities import classify_competition  # noqa: E402
from edgefactory.config import GATES  # noqa: E402
from edgefactory.fade import (  # noqa: E402
    FADE_VIEW, fade_edge_metadata, ml_fade_settled_sql,
)
from edgefactory.phase5_registry_guard import (  # noqa: E402
    inspect_operational_registry,
    preserve_live_ml_payload,
)
from edgefactory.ml_fade_research import model_key  # noqa: E402

DB = ROOT / "localdata" / "warehouse.duckdb"
OUT = ROOT / "localdata" / "edges_consensus.json"
RESEARCH_OUT = ROOT / "localdata" / "edges_consensus_research.json"
ML_PREDS_PATH = ROOT / "localdata" / "ml_meta_predictions.csv.gz"
ML_RESEARCH_PREDS_PATH = ROOT / "localdata" / "ml_meta_predictions_research.csv.gz"
ACTIVATION_ROOT = ROOT / "localdata" / "phase5_activation"

# Cold-cache guard: certification must never silently run on a warehouse with
# insufficient PRE-SPLIT settled history (the L9 cold-cache trap). The file may
# exist (or be a fresh build) while the settled tables are nearly empty — the
# old code only checked DB.exists(), so a cold cache certified nothing and the
# write_registry regression guard then PRESERVED stale edges as if re-validated.
MIN_PRE_SPLIT_SETTLED = 500   # well above min_n_train (340); trains on this


def _count_pre_split_settled(con, view: str, split: str) -> int:
    try:
        n = con.sql(
            f"SELECT count(*) FROM {view} WHERE date < CAST('{split}' AS DATE)"
        ).fetchone()[0]
        return int(n or 0)
    except Exception:
        return -1


def _cold_cache_check(con, split: str) -> bool:
    """Return True if the cache is too cold to certify; prints loudly."""
    tables = [
        ("forebet_settled", "forebet"),
        ("zulubet_settled", "zulubet"),
        ("statarea_settled", "statarea"),
        ("scoutingstats_settled", "scoutingstats"),
        ("vitibet_settled", "vitibet"),
    ]
    cold = False
    for view, name in tables:
        if not _table_exists(con, view):
            continue
        n = _count_pre_split_settled(con, view, split)
        if n < 0:
            continue
        if n < MIN_PRE_SPLIT_SETTLED:
            cold = True
            print(f"⚠️  COLD-CACHE: {name} settled pre-split rows = {n} "
                  f"(< {MIN_PRE_SPLIT_SETTLED}) — cannot certify on this cache.")
    return cold


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


def _atomic_registry_write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _score_live_model(df, live_model: object) -> list[float] | None:
    """Score the warehouse rows with the model currently in the live registry.

    The fresh training fit is research-only for decay purposes; decay and
    bench monitoring must use predictions from the current live scorer.

    The incumbent is scored on ITS OWN feature contract, never the
    candidate's: retraining the candidate (e.g. dropping the leaking
    ht_diff/ht_total features) must not silently stop the incumbent
    prediction export and send the decay monitor fail-closed on every ML
    edge. The live payload's own feature_cols drive the matrix, and the
    columns must exist on the frame (they are still computed even when the
    candidate no longer trains on them).
    """
    if not isinstance(live_model, dict):
        return None
    live_cols = live_model.get("feature_cols")
    if not isinstance(live_cols, list) or not live_cols:
        return None
    if any(col not in df.columns for col in live_cols):
        return None
    try:
        coefficients = np.asarray(live_model.get("coef"), dtype=float)
        matrix = df[live_cols].to_numpy(dtype=float)
        intercept = float(live_model["intercept"])
        if coefficients.ndim != 1 or coefficients.shape[0] != matrix.shape[1]:
            return None
        logits = matrix @ coefficients + intercept
        if not np.isfinite(logits).all():
            return None
        probabilities = 1.0 / (1.0 + np.exp(-np.clip(logits, -700.0, 700.0)))
        if not np.isfinite(probabilities).all():
            return None
        return probabilities.tolist()
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def write_registry(payload: dict) -> bool:
    """Write research output separately and merge only safe operational edges.

    The legacy fit still runs unchanged for diagnostics, and its full candidate
    payload is written to ``edges_consensus_research.json``. The operational
    registry accepts the newly mined non-ML edges while carrying forward the
    *current* model and ML rule entries byte-for-value. It never copies the
    Phase 5 baseline over a mismatch, nor adopts a new legacy model/cut set.

    A missing or unreadable live registry is not reconstructed from the
    candidate or baseline: the write is refused so a missing incumbent or
    existing bench cannot be silently cleared. The existing cold-cache
    regression-to-zero guard remains in force.

    Returns True if the safe operational registry was written, False if it was
    kept unchanged.
    """
    try:
        _atomic_registry_write(RESEARCH_OUT, payload)
        print(f"\nlegacy candidate kept research-only -> {RESEARCH_OUT}")
    except Exception as exc:  # research output must not disrupt the safe path
        print(f"WARNING: could not persist separate legacy research payload ({type(exc).__name__})")

    new_certified = _count_certified(payload.get("edges", []))
    existing_certified = _existing_certified_count()

    if new_certified == 0 and existing_certified > 0:
        print(
            "\n⚠️  REGRESSION GUARD: this run certified 0 edges, but the existing "
            f"registry already holds {existing_certified} certified edge(s)."
        )
        print("    Keeping the existing registry to avoid clobbering certified edges.")
        print(f"    Preserved file: {OUT}")
        return False

    if not OUT.exists():
        print(
            f"\nPHASE5_REGISTRY_GUARD blocked operational write: live registry is missing; "
            f"candidate model/cuts remain research-only ({RESEARCH_OUT})."
        )
        return False
    try:
        current = json.loads(OUT.read_text(encoding="utf-8"))
        if not isinstance(current, dict) or not isinstance(current.get("edges"), list):
            raise ValueError("live registry must contain an edge list")
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        print(
            f"\nPHASE5_REGISTRY_GUARD blocked operational write: live registry unreadable "
            f"({type(exc).__name__}); candidate remains research-only."
        )
        return False

    safe_payload, merge = preserve_live_ml_payload(payload, current)
    guard = inspect_operational_registry(current, ACTIVATION_ROOT)
    if guard["ok"]:
        print(
            "PHASE5_REGISTRY_GUARD incumbent verified; "
            f"preserving model_key={merge['preserved_model_key']} and "
            f"{merge['preserved_ml_edge_count']} current ML edge(s)."
        )
    else:
        print(
            "PHASE5_REGISTRY_GUARD BASELINE MISMATCH; no model/cut repair or adoption. "
            "The current ML payload is preserved verbatim, ML scoring remains blocked, "
            f"and unrelated non-ML edges may update. reason={guard['reason']}"
        )

    _atomic_registry_write(OUT, safe_payload)
    print(
        f"\nwritten -> {OUT} (candidate_certified={new_certified}; "
        f"operational_non_ml={merge['accepted_non_ml_edge_count']}; "
        f"preserved_ml={merge['preserved_ml_edge_count']})"
    )
    return True


def _table_exists(con, name: str) -> bool:
    try:
        con.execute(f"SELECT 1 FROM {name} LIMIT 0")
        return True
    except Exception:
        return False


def _table_columns(con, name: str) -> set[str]:
    try:
        return {str(row[1]) for row in con.execute(f"PRAGMA table_info('{name}')").fetchall()}
    except Exception:
        return set()


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
        ("prosoccer_settled",  "prosoccer",  "1x2"),
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
    if _table_exists(con, "prosoccer_settled"):
        SINGLE_SOURCE_SPECS.append(("prosoccer_settled", "prosoccer", "ou_2.5",
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
# NOTE: capture-forward sources (prosoccer) can only join after their settled
# history satisfies the same walk-forward gates as every other source; until
# then the weighted rules surface as shadow candidates and never fire live.
_WEIGHTED_SOURCES_1X2   = ["forebet", "zulubet", "statarea", "vitibet", "scoutingstats",
                           "prosoccer"]
_WEIGHTED_SOURCES_OU25  = ["forebet", "statarea", "scoutingstats", "prosoccer"]
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
            columns = _table_columns(con, view)
            if {"odd1", "oddx", "odd2"}.issubset(columns):
                odds_expr = (
                    "CASE pick WHEN 'home' THEN odd1 "
                    "WHEN 'draw' THEN oddx ELSE odd2 END"
                )
            else:
                # Probability-only sources (notably Statarea and Vitibet) are
                # valid voters. Missing source odds must reduce price coverage,
                # not make the entire weighted consensus query disappear.
                odds_expr = "NULL::DOUBLE"
            unions.append(f"""
                SELECT date, hkey, akey, home, away, outcome, league,
                       pick, pmax/{scale} AS prob,
                       {odds_expr} AS pick_odds,
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

            # ONE rung, not six. `weighted_consensus_score` returns exactly
            # 1.0 whenever the contributing sources agree, and the loop only
            # keeps unanimous matches, so every threshold from 0.55 upward
            # selected the byte-identical match set: the six
            # `weighted-1x2 w_score>=0.55..0.80` entries were the same rule
            # six times (44,728 rows / 50.3% / +9.3% each). 0.55 is kept as
            # the single threshold because it is the rung that actually
            # describes the selection; higher w_score rungs only become
            # meaningful if non-unanimous scoring is ever admitted.
            for w_thr in (0.55,):
                rule_name = f"weighted-1x2 w_score>={w_thr:.2f}"
                qualifying: list[dict] = []
                for match in matches.values():
                    # Global source availability is not per-fixture consensus:
                    # require at least two independent votes on this match.
                    if len(match["votes"]) < 2:
                        continue
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
               pick_odds,
               -- orphaned-data harvest (consensus3 carries these now)
               ht_hs, ht_gs, p1_ht, px_ht, p2_ht,
               kelly, pred_hs, pred_gs, goalsavg,
               p_ng, p_under, p_gg,
               sa_p1_ht, sa_px_ht, sa_p2_ht
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

    # Scale fix (2026-08-10): warehouse consensus probs are PERCENT (0-100);
    # the live path feeds 0-1. Normalize to 0-1 here so train == inference.
    # Without this the certified model could never fire live (max ml_p ~7%).
    for col in ('fb_p', 'zb_p', 'sa_p'):
        df[col] = np.where(df[col] > 1.5, df[col] / 100.0, df[col])
    for col in ('p1_ht', 'px_ht', 'p2_ht', 'p_ng', 'p_under', 'p_gg'):
        if col in df.columns:
            df[col] = np.where(df[col] > 1.5, df[col] / 100.0, df[col])
    for col in ('sa_p1_ht', 'sa_px_ht', 'sa_p2_ht'):
        if col in df.columns:
            df[col] = np.where(df[col] > 1.5, df[col] / 100.0, df[col])

    probs = df[['fb_p', 'zb_p', 'sa_p']].values
    df['avg_p'] = np.mean(probs, axis=1)
    df['min_p'] = np.min(probs, axis=1)
    df['std_p'] = np.std(probs, axis=1)

    df['is_home'] = (df['pick'] == 'home').astype(int)
    df['is_away'] = (df['pick'] == 'away').astype(int)

    df['cat'] = df['league'].apply(classify_competition)
    for cat in ['friendly', 'youth', 'women', 'cup', 'league']:
        df[f'cat_{cat}'] = (df['cat'] == cat).astype(int)

    # --- orphaned-data features (eyes-open harvest) ---
    # HT win prob of the majority pick (forebet HT probs, 0-1)
    def _ht_pick_prob(row):
        p1h, pxh, p2h = row.get('p1_ht'), row.get('px_ht'), row.get('p2_ht')
        if p1h is None or pxh is None or p2h is None:
            return 0.5
        idx = {'home': 0, 'draw': 1, 'away': 2}.get(row['pick'], 1)
        v = (p1h, pxh, p2h)[idx]
        return float(v) if v == v else 0.5  # NaN guard
    df['ht_p'] = df.apply(_ht_pick_prob, axis=1)

    # Phase A (2026-08-10): statarea half-time win prob of the majority pick
    def _sa_ht_pick_prob(row):
        p1h, pxh, p2h = row.get('sa_p1_ht'), row.get('sa_px_ht'), row.get('sa_p2_ht')
        if p1h is None or pxh is None or p2h is None:
            return 0.5
        idx = {'home': 0, 'draw': 1, 'away': 2}.get(row['pick'], 1)
        v = (p1h, pxh, p2h)[idx]
        return float(v) if v == v else 0.5
    df['sa_ht_p'] = df.apply(_sa_ht_pick_prob, axis=1)

    # HT score state
    df['ht_diff'] = pd.to_numeric(df['ht_hs'], errors='coerce').fillna(0) - pd.to_numeric(df['ht_gs'], errors='coerce').fillna(0)
    df['ht_total'] = pd.to_numeric(df['ht_hs'], errors='coerce').fillna(0) + pd.to_numeric(df['ht_gs'], errors='coerce').fillna(0)

    # Kelly (forebet staking signal; raw, can be negative)
    df['kelly'] = pd.to_numeric(df['kelly'], errors='coerce').fillna(0.0)

    # predicted score totals/diff (forebet)
    df['pred_total'] = pd.to_numeric(df['pred_hs'], errors='coerce').fillna(0) + pd.to_numeric(df['pred_gs'], errors='coerce').fillna(0)
    df['pred_diff'] = pd.to_numeric(df['pred_hs'], errors='coerce').fillna(0) - pd.to_numeric(df['pred_gs'], errors='coerce').fillna(0)

    # goalsavg, BTTS-no, under probs
    df['goalsavg'] = pd.to_numeric(df['goalsavg'], errors='coerce').fillna(0.0)
    df['p_ng'] = pd.to_numeric(df['p_ng'], errors='coerce').fillna(0.0)
    df['p_under'] = pd.to_numeric(df['p_under'], errors='coerce').fillna(0.0)
    df['p_gg'] = pd.to_numeric(df['p_gg'], errors='coerce').fillna(0.0)

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
        'rolling_hit_rate',
        'ht_p',
        # ht_diff / ht_total are DROPPED (diagnosis_no_autobets_2026-10-06
        # §3.2 / fix #6): they are the actual half-time score, i.e. the
        # target leaking into training, and they are pinned to 0 at serve
        # (FROZEN_FEATURE_COLS / checkpoint ⑫), so they can only inflate the
        # research fit and are unreachable live. Any earlier certified number
        # that leaned on them was not reachable at bet time.
        'kelly', 'pred_total', 'pred_diff',
        'goalsavg', 'p_ng', 'p_under',
        'sa_ht_p', 'p_gg',
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
    
    # Keep the just-fitted candidate export separate from the operational
    # prediction file. Decay/bench monitoring reads only the latter and it must
    # be scored by the model that is still present in edges_consensus.json.
    candidate_predictions = df[['date', 'home', 'away', 'ml_p', 'pick']].copy()
    candidate_predictions['model_key'] = model_key(payload)
    try:
        ML_RESEARCH_PREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        candidate_predictions.to_csv(
            ML_RESEARCH_PREDS_PATH, index=False, compression="gzip"
        )
        print(
            f"Saved {len(df):,} candidate ML predictions (research-only) -> "
            f"{ML_RESEARCH_PREDS_PATH}"
        )
    except Exception as exc:
        print(f"Failed to save separate candidate ML predictions: {type(exc).__name__}")

    incumbent_registry = None
    try:
        incumbent_registry = json.loads(OUT.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        pass
    live_model = (
        incumbent_registry.get("ml_model")
        if isinstance(incumbent_registry, dict) else None
    )
    incumbent_probabilities = _score_live_model(df, live_model)
    if incumbent_probabilities is None:
        print(
            "Incumbent ML prediction export not refreshed: live model missing or "
            "incompatible; decay monitor will fail closed for ML edges."
        )
    else:
        incumbent_predictions = df[['date', 'home', 'away', 'pick']].copy()
        incumbent_predictions['ml_p'] = incumbent_probabilities
        incumbent_predictions['model_key'] = model_key(live_model)
        try:
            ML_PREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
            incumbent_predictions.to_csv(
                ML_PREDS_PATH, index=False, compression="gzip"
            )
            print(
                f"Saved {len(df):,} live-incumbent ML predictions "
                f"(model_key={model_key(live_model)}) -> {ML_PREDS_PATH}"
            )
        except Exception as exc:
            print(f"Failed to save incumbent ML predictions: {type(exc).__name__}")

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

    if _table_exists(con, "windrawwin") and _table_exists(con, "results_donor"):
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW windrawwin_settled AS
                WITH ww AS (SELECT DISTINCT ON (date, hkey, akey) * FROM windrawwin
                            WHERE pick IN ('home','draw','away')),
                     rd AS (SELECT DISTINCT ON (date, hkey, akey) * FROM results_donor)
                SELECT ww.*, rd.hs, rd.gs, rd.result_source,
                       ww.pick AS ww_pick,
                       CASE WHEN rd.hs > rd.gs THEN 'home'
                            WHEN rd.hs < rd.gs THEN 'away' ELSE 'draw' END AS outcome
                FROM ww JOIN rd USING (date, hkey, akey)
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

    # soccervista: same categorical profile as windrawwin (1X2 pick, no probs,
    # no scores). Settle against the prioritized multi-source donor so current
    # evidence can mature while Forebet is unavailable.
    if _table_exists(con, "soccervista") and _table_exists(con, "results_donor"):
        try:
            con.execute("""
                CREATE OR REPLACE TEMP VIEW soccervista_settled AS
                WITH sv AS (SELECT DISTINCT ON (date, hkey, akey) * FROM soccervista
                            WHERE pick IN ('home','draw','away')),
                     rd AS (SELECT DISTINCT ON (date, hkey, akey) * FROM results_donor)
                SELECT sv.*, rd.hs, rd.gs, rd.result_source,
                       sv.pick AS sv_pick,
                       CASE WHEN rd.hs > rd.gs THEN 'home'
                            WHEN rd.hs < rd.gs THEN 'away' ELSE 'draw' END AS outcome
                FROM sv JOIN rd USING (date, hkey, akey)
            """)
            made.add("soccervista_settled")
            if _table_exists(con, "v_consensus2"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus2_soccervista_confirm AS
                    WITH c2 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus2),
                         sv AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, sv_pick
                                FROM soccervista_settled)
                    SELECT c2.*, sv.sv_pick
                    FROM c2 JOIN sv USING (date, home, away)
                """)
                made.add("consensus2_soccervista_confirm")
            if _table_exists(con, "v_consensus3"):
                con.execute("""
                    CREATE OR REPLACE TEMP VIEW consensus3_soccervista_confirm AS
                    WITH c3 AS (SELECT DISTINCT ON (date, home, away) * FROM v_consensus3),
                         sv AS (SELECT DISTINCT ON (date, home, away)
                                      date, home, away, sv_pick
                                FROM soccervista_settled)
                    SELECT c3.*, sv.sv_pick
                    FROM c3 JOIN sv USING (date, home, away)
                """)
                made.add("consensus3_soccervista_confirm")
        except Exception as exc:
            print(f"skipped soccervista confirmation views: {exc}")

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

    if "consensus2_soccervista_confirm" in made:
        for thr in (60, 65, 70, 75):
            results.append(evaluate(
                con, f"2way+soccervista-confirms avg_p>={thr}", "consensus2_soccervista_confirm",
                f"fb_pick = zb_pick AND fb_pick = sv_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb})/2)*100 >= {thr}",
                split,
            ))
    else:
        if not _table_exists(con, "soccervista"):
            print("skipped soccervista confirmation: no soccervista data")

    if "consensus3_soccervista_confirm" in made:
        for thr in (60, 65, 70):
            results.append(evaluate(
                con, f"3way+soccervista-confirms avg_p>={thr}", "consensus3_soccervista_confirm",
                f"fb_pick = zb_pick AND zb_pick = sa_pick AND fb_pick = sv_pick "
                f"AND ((fb_p/{sfb} + zb_p/{szb} + sa_p/{ssa})/3)*100 >= {thr}",
                split,
            ))


# Current-source re-mine. Keep the legacy statistical/ML helpers above for
# historical receipts and frozen-incumbent consumers; the daily entry point
# below no longer fits Forebet electorates or the Forebet-feature ML model.
POST_FOREBET_START = "2026-06-13"
REMINE_SOURCES = (
    "zulubet", "statarea", "vitibet", "scoutingstats", "prosoccer",
    "betclan", "bzzoiro", "predictz", "windrawwin", "soccervista",
    "bettingclosed", "freesupertips", "afootballreport",
)
REMINE_MARKETS = tuple(dict.fromkeys(
    get_bettable_markets() + ["ou_1.5", "ou_3.5", "ou_4.5"]))
REMINE_THRESHOLDS = (0, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90)


def _number(value):
    try:
        value = float(value)
        return value if math.isfinite(value) else None
    except (TypeError, ValueError):
        return None


def _score_pair(row, prefix=""):
    pair = [_number(row.get(prefix + field)) for field in ("hs", "gs")]
    return tuple(int(v) for v in pair) if all(
        v is not None and v >= 0 and v.is_integer() for v in pair) else None


def _remine_key(row):
    home, away = source_team_key(row.get("home")), source_team_key(row.get("away"))
    if min(len(home), len(away)) < 4 or home == away:
        return None
    return str(row["date"])[:10], home, away


def _remine_signal(row, market):
    """Observed probabilities or categorical tips; never turn streaks into p.

    Warehouse sources have different units, so infer one scale from the full
    1X2 vector (when available), otherwise from the probability field itself.
    A full vector must be finite, bounded and sum approximately to one.
    """
    triple = [_number(row.get(c)) for c in ("p1", "px", "p2")]
    scale = 100.0 if any(v is not None and v > 1.5 for v in triple) else 1.0
    if market in ("1x2", "ht_1x2"):
        fields = ("p1", "px", "p2") if market == "1x2" else ("p1_ht", "px_ht", "p2_ht")
        values = [_number(row.get(c)) for c in fields]
        if market == "ht_1x2":
            scale = 100.0 if any(v is not None and v > 1.5 for v in values) else 1.0
        if all(v is not None and 0 <= v <= scale for v in values):
            probs = dict(zip(("home", "draw", "away"), (v / scale for v in values)))
            if abs(sum(probs.values()) - 1) > 0.05:
                return None
            best = max(probs.values())
            leaders = [side for side, prob in probs.items() if prob == best]
            return (leaders[0], probs) if len(leaders) == 1 else None
        if market != "1x2":
            return None
        # A categorical tip is eligible for the no-probability-floor test only.
        raw = str(row.get("pick") or row.get("pick_1x2") or row.get("tip") or "").lower()
        side = {"1": "home", "x": "draw", "2": "away"}.get(raw, raw)
        return (side, None) if side in ("home", "draw", "away") else None
    field = {"ou_1.5": "p_o15", "ou_2.5": "p_o25", "ou_3.5": "p_o35",
             "ou_4.5": "p_o45", "btts": "p_gg", "ht_ou_1.5": "p_o15_ht",
             "ht_ou_2.5": "p_o25_ht"}[market]
    value = _number(row.get(field))
    yes, no = ("yes", "no") if market == "btts" else ("over", "under")
    if value is not None:
        if all(v is None for v in triple):
            scale = 100.0 if value > 1.5 else 1.0
        value /= scale
        if not 0 <= value <= 1 or value == 0.5:
            return None
        return (yes if value > 0.5 else no, {yes: value, no: 1 - value})
    raw = str(row.get("pick_btts") if market == "btts" else
              row.get("pick_ou") if market == "ou_2.5" else "").lower()
    raw = {"gol": "yes", "nogol": "no", "over 2.5": "over", "under 2.5": "under"}.get(raw, raw)
    return (raw, None) if raw in (yes, no) else None


def _remine_outcome(scores, market):
    pair = scores.get("ht" if market.startswith("ht_") else "ft")
    if pair is None:
        return None
    hs, gs = pair
    if market.endswith("1x2"):
        return "home" if hs > gs else "away" if hs < gs else "draw"
    if market == "btts":
        return "yes" if hs > 0 and gs > 0 else "no"
    line = float(market.rsplit("_", 1)[1])
    return "over" if hs + gs > line else "under"


def _remine_odds(rows, market, side):
    fields = {"1x2": {"home": ("odd1",), "draw": ("oddx",), "away": ("odd2",)},
              "ou_2.5": {"over": ("odd_over", "odd_o25"), "under": ("odd_under", "odd_u25")},
              "btts": {"yes": ("odd_gg",), "no": ("odd_ng",)}}.get(market, {})
    # Conservative minimum for the SAME side/market only. Never use an
    # opposing vote's odds, fair odds or an invented complement price.
    prices = [_number(row.get(field)) for row in rows for field in fields.get(side, ())]
    prices = [v for v in prices if v is not None and v > 1]
    return min(prices) if prices else None


def remine_current_sources(con, *, start, split, as_of):
    """All observed non-Forebet subsets, including single and dissent tests.

    Results are candidate research, not automatically served authorization.
    The same train/validation statistics and gates are used, but absent ROI
    cannot pass. Full source keys and scores replace legacy nine-char joins.
    """
    for value in (start, split, as_of):
        if date.fromisoformat(value).isoformat() != value:
            raise ValueError("dates must be ISO YYYY-MM-DD")
    if not POST_FOREBET_START <= start < split < as_of:
        raise ValueError("require 2026-06-13 <= start < split < as_of")
    coverage, source_rows = {}, {}
    for source in (*REMINE_SOURCES, "betexplorer"):
        # Raw predictions must win over a pre-settled convenience view:
        # another independent donor may settle rows absent from that view.
        table = next((t for t in (source, source + "_raw", source + "_settled")
                      if _table_exists(con, t)), None)
        if table is None:
            coverage[source] = {"status": "missing_table", "rows": 0}
            continue
        columns = _table_columns(con, table)
        if not {"date", "home", "away"}.issubset(columns):
            coverage[source] = {"status": "missing_identity_columns", "rows": 0}
            continue
        cursor = con.execute(f"SELECT * FROM {table} WHERE TRY_CAST(date AS DATE) >= ? "
                             "AND TRY_CAST(date AS DATE) < ?", [start, as_of])
        names = [col[0] for col in cursor.description]
        rows = [dict(zip(names, values)) for values in cursor.fetchall()]
        source_rows[source] = rows
        coverage[source] = {"status": "present" if rows else "no_rows_in_era", "table": table,
                            "rows": len(rows), "market_votes": {m: 0 for m in REMINE_MARKETS}}

    scores = defaultdict(lambda: defaultdict(set))
    # Only self-scoring donors. In particular do NOT use results_donor or
    # categorical *_settled scores which may have been inherited from Forebet.
    donors = {"zulubet", "statarea", "vitibet", "scoutingstats", "prosoccer",
              "bettingclosed", "betexplorer"}
    for source in donors:
        for row in source_rows.get(source, []):
            key = _remine_key(row)
            if key is None or str(row.get("result_source") or source) == "forebet":
                continue
            for period, prefix in (("ft", ""), ("ht", "ht_")):
                pair = _score_pair(row, prefix)
                if pair is not None:
                    scores[key][period].add(pair)
    resolved = {key: {period: next(iter(values)) for period, values in periods.items()
                      if len(values) == 1} for key, periods in scores.items()}
    observations = defaultdict(dict)
    ambiguous = set()
    for source in REMINE_SOURCES:
        for row in source_rows.get(source, []):
            key = _remine_key(row)
            if key is None:
                continue
            for market in REMINE_MARKETS:
                signal = _remine_signal(row, market)
                if signal is None:
                    continue
                identity = (key, market, source)
                bucket = observations[(key, market)]
                vote = {"side": signal[0], "probs": signal[1], "row": row}
                previous = bucket.get(source)
                if previous and (previous["side"], previous["probs"], previous["row"].get("kickoff")) != (
                        vote["side"], vote["probs"], row.get("kickoff")):
                    ambiguous.add(identity)
                bucket[source] = vote
    candidates = defaultdict(list)
    recipes = {}
    for (key, market), all_votes in observations.items():
        votes = {source: vote for source, vote in all_votes.items()
                 if (key, market, source) not in ambiguous}
        for source in votes:
            coverage[source]["market_votes"][market] += 1
        outcome = _remine_outcome(resolved.get(key, {}), market)
        if outcome is None:
            continue
        names = sorted(votes)
        for size in range(1, len(names) + 1):
            for subset in combinations(names, size):
                electorate = [votes[source] for source in subset]
                counts = Counter(v["side"] for v in electorate)
                strategies = []
                if size == 1 or len(counts) == 1:
                    strategies.append(("single" if size == 1 else "unanimous", None, electorate[0]["side"]))
                else:
                    side, n = counts.most_common(1)[0]
                    if n > size / 2:
                        strategies.append(("majority", None, side))
                    strategies.extend(("disagree_follow", source, votes[source]["side"]) for source in subset)
                for strategy, follow, side in strategies:
                    recipe = (market, subset, strategy, follow)
                    recipes[recipe] = True
                    contributing = [votes[follow]] if follow else electorate
                    probability = (100 * sum(v["probs"][side] for v in contributing) / len(contributing)
                                   if all(v["probs"] is not None for v in contributing) else None)
                    row0 = electorate[0]["row"]
                    candidates[recipe].append({"date": key[0], "home": row0["home"], "away": row0["away"],
                                               "pick": side, "outcome": outcome,
                                               "pick_odds": _remine_odds([v["row"] for v in electorate], market, side),
                                               "avg_p": probability})
    results = []
    for recipe in sorted(recipes, key=str):
        market, subset, strategy, follow = recipe
        frame = pd.DataFrame(candidates[recipe])
        con.register("post_forebet_slice", frame)
        for threshold in REMINE_THRESHOLDS:
            where = "1=1" if threshold == 0 else f"avg_p >= {threshold}"
            name = f"{market} {strategy}[{'+'.join(subset)}]" + (f" follow={follow}" if follow else "") + f" avg_p>={threshold}"
            edge = evaluate(con, name, "post_forebet_slice", where, split, market)
            holds = []
            for period, minimum in (("train", GATES.min_n_train), ("valid", GATES.min_n_valid)):
                st = edge[period]
                if st["n"] < minimum:
                    holds.append(f"{period}_sample_below_{minimum}")
                # Requiring priced samples prevents None ROI (or one quote)
                # from masquerading as validated betting profitability.
                if st["n_priced"] < minimum:
                    holds.append(f"{period}_priced_sample_below_{minimum}")
                if st["roi"] is None:
                    holds.append(f"{period}_roi_unavailable")
            if edge["status"] != "certified":
                holds.append("statistical_gates_not_met")
            edge.update({"status": "candidate", "statistical_gates_passed": not holds,
                         "holds": holds + ["new_predicate_requires_serving_validation"],
                         "sources": list(subset), "strategy": strategy, "follow_source": follow,
                         "threshold": threshold, "view": None, "where": None})
            # post_forebet_slice is a transient evaluation relation, NOT a
            # persisted operational view. Never publish an un-recreatable rule.
            results.append(edge)
        con.unregister("post_forebet_slice")
    market_coverage = {m: {"usable_votes": sum(c.get("market_votes", {}).get(m, 0) for c in coverage.values()),
                           "tested_rules": sum(e["market"] == m for e in results)} for m in REMINE_MARKETS}
    for cell in market_coverage.values():
        cell["status"] = ("tested" if cell["tested_rules"] else
                          "no_unconflicted_results" if cell["usable_votes"] else "no_usable_signals")
    return {"status": "mined_candidates" if results else "no_gradeable_prediction_history",
            "mining_era": "post_forebet", "start": start, "split": split, "as_of_exclusive": as_of,
            "gates": vars(GATES), "excluded_voters": ["forebet"], "excluded_result_donors": ["forebet"],
            "sources": coverage, "markets": market_coverage, "edges": results,
            "ambiguous_source_market_observations": len(ambiguous),
            "conflicting_result_periods": sum(len(v) > 1 for p in scores.values() for v in p.values()),
            "settled_fixture_markets": len({(key, market) for key, market in observations
                                            if _remine_outcome(resolved.get(key, {}), market) is not None}),
            "activation": "research_only; existing live registry and frozen model unchanged",
            "limitations": ["Threshold grid is model selection, not untouched forward evidence.",
                            "Source quotes are retrospective donor prices, not execution-safe ROI.",
                            "No probability is inferred from categorical tips or streak percentages."]}


def _publish_remine_results(payload):
    """Expose research passes without requiring an artifact download.

    Numbered notice batches are readable via the checks API; the human summary
    is a second view of the same report, never a serving/activation registry.
    """
    passed = [e for e in payload["edges"] if e["statistical_gates_passed"]]
    receipt = {key: value for key, value in payload.items() if key != "edges"}
    receipt.update(source_rows={s: c["rows"] for s, c in payload["sources"].items()},
                   tested_rules=len(payload["edges"]), statistical_gates_passed=len(passed))
    summary = ["## Post-Forebet re-mine — research only",
               "These passes are not approved live rules. Shared fixtures and searched "
               "thresholds are not independent forward evidence; donor-price ROI is retrospective.",
               "```json", json.dumps(receipt, sort_keys=True, indent=2), "```",
               "### Passing candidates",
               "Train/validation cells: n / priced n / hit / ROI / Wilson lower bound.",
               "| Rule | Train | Validation | Remaining holds |",
               "| --- | --- | --- | --- |"]
    summary_size = sum(len(line.encode("utf-8")) + 1 for line in summary)
    for edge in passed:
        cells = [str(edge["rule"])]
        for period in ("train", "valid"):
            stats = edge[period]
            cells.append(" / ".join(str(stats.get(k)) for k in
                                    ("n", "n_priced", "hit", "roi", "wilson_lb")))
        cells.append(", ".join(edge["holds"]))
        line = "| " + " | ".join(c.replace("|", "&#124;").replace("\n", " ").replace("\r", " ")
                                  for c in cells) + " |"
        summary_size += len(line.encode("utf-8")) + 1
        if summary_size > 900_000:  # GitHub caps a step summary at 1 MiB.
            summary.append("Summary table shortened; ALL passing candidates remain in the numbered check annotations.")
            break
        summary.append(line)
    if not passed:
        summary.append("No candidates passed the statistical and priced-sample gates.")
    summary.append("Full passing-candidate records, including electorates, strategies, thresholds "
                   "and holds, are in the numbered Post-Forebet passing candidates check annotations.")
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        try:
            with open(summary_path, "a", encoding="utf-8") as handle:
                handle.write("\n" + "\n\n".join(summary[:7]) + "\n" + "\n".join(summary[7:]) + "\n")
        except OSError as exc:
            print(f"Could not write GitHub step summary ({type(exc).__name__}); research report retained.")

    if os.environ.get("GITHUB_ACTIONS") != "true":
        for edge in passed:
            print("Passing research candidate: " + json.dumps(edge, sort_keys=True))
        return

    def notice(title, data):
        # Escape workflow-command data, including literal provider %0A tokens.
        text = json.dumps(data, sort_keys=True, separators=(",", ":")).replace("%", "%25")
        print(f"::notice title={title}::" + text)

    notice("Post-Forebet re-mine", receipt)
    batches, batch, size = [], [], 0
    for edge in passed:
        length = len(json.dumps(edge, sort_keys=True).replace("%", "%25").encode("utf-8")) + 1
        if batch and size + length > 45_000:  # Stay below the 64 KiB annotation limit.
            batches.append(batch)
            batch, size = [], 0
        batch.append(edge)
        size += length
    if batch:
        batches.append(batch)
    for index, batch in enumerate(batches, 1):
        notice(f"Post-Forebet passing candidates {index}/{len(batches)}",
               {"part": index, "parts": len(batches), "research_only": True,
                "passing_candidates": batch})


def main():
    ap = argparse.ArgumentParser(description="Re-mine current non-Forebet electorates using retained data only")
    ap.add_argument("--start", default=POST_FOREBET_START)
    ap.add_argument("--as-of", default=date.today().isoformat(), help="exclusive; never include the incomplete current day")
    ap.add_argument("--split", default=None, help="chronological train/validation boundary (default: as-of minus 28 days)")
    ap.add_argument("--output", type=Path, default=RESEARCH_OUT)
    args = ap.parse_args()
    try:
        for value in (args.start, args.as_of, args.split or args.as_of):
            if date.fromisoformat(value).isoformat() != value:
                raise ValueError("dates must be ISO YYYY-MM-DD")
        split = args.split or (date.fromisoformat(args.as_of) - timedelta(days=28)).isoformat()
    except ValueError as exc:
        ap.error(str(exc))
    if args.output.resolve() == OUT.resolve():
        ap.error("the re-mine output cannot overwrite the operational registry")
    if not POST_FOREBET_START <= args.start < split < args.as_of:
        ap.error("require 2026-06-13 <= start < split < as-of")
    if DB.exists():
        con = duckdb.connect(str(DB), read_only=True)
    else:
        from edgefactory.warehouse import connect
        con = connect()  # Existing CSV views; no fetch, rebuild or operational write.
    try:
        payload = remine_current_sources(con, start=args.start, split=split, as_of=args.as_of)
    finally:
        con.close()
    _atomic_registry_write(args.output, payload)
    print(f"Post-Forebet re-mine: {args.start} <= train < {split} <= validation < {args.as_of}")
    for source, coverage in payload["sources"].items():
        print(f"  {source}: {coverage['status']} rows={coverage['rows']}")
    for market, coverage in payload["markets"].items():
        print(f"  {market}: usable_votes={coverage['usable_votes']} tested_rules={coverage['tested_rules']}")
    print(f"Status: {payload['status']}")
    print(f"Candidate tests: {len(payload['edges'])}; statistical gates passed: "
          f"{sum(e['statistical_gates_passed'] for e in payload['edges'])}")
    print(f"Report: {args.output}. Live registry/model unchanged; no serving approval inferred.")
    _publish_remine_results(payload)


def _print_k_coverage_diagnostic() -> None:
    """Read-only Phase 5 K coverage report, printed in every miner run.

    The forward era's 32-column contract is fed by sources that are partly
    dark; this block says which ones, and when a candidate fit becomes due, so
    a returning feed is visible in the log the day it lands. It runs the same
    read-only explain path as ``fit_phase5_candidate.py --explain`` and can
    never affect the mine — diagnostics, not pipeline state.
    """
    script = Path(__file__).resolve().parent / "fit_phase5_candidate.py"
    if not script.exists():
        return
    print("\n--- Phase 5 K-contract coverage (read-only) ---")
    # Resolve imports and relative localdata paths from the repo root, not from
    # whatever cwd the miner happened to be launched in.
    root = script.parent.parent
    env = dict(os.environ)
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(root / "src") + (os.pathsep + existing_path if existing_path else "")
    try:
        proc = subprocess.run(
            [sys.executable, str(script), "--explain"],
            capture_output=True, text=True, timeout=180, cwd=str(root), env=env,
        )
    except Exception as exc:  # pragma: no cover - diagnostics must never gate
        print(f"(K coverage diagnostic skipped: {type(exc).__name__})")
        return
    output = (proc.stdout or "").strip()
    if output:
        print(output)
    if proc.returncode not in (0, 1, 2, 3, 4) and proc.stderr:
        print(f"(explain exited {proc.returncode}) {proc.stderr.strip()[:400]}")


if __name__ == "__main__":
    main()
