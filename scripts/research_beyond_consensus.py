#!/usr/bin/env python3
"""Offline research: beyond-source-consensus prematch baselines (READ-ONLY).

Purpose
-------
Workstream B first experiment: build a fixture-level research dataset from the
committed prediction archives, evaluate small feature groups against market
and consensus baselines under chronological, fixture-grouped evaluation —
without touching any operational output (no picks, no registries, no
notifications; writes only under ``research/``).

What it reads (all committed, no network)
-----------------------------------------
* ``localdata/forebet.csv.gz``  — probabilities + provider-average 1x2 odds
  + provider prematch extras; final scores; 2024-01-01 → 2026-06-12.
* ``localdata/zulubet.csv.gz``  — probabilities + tip odds; final scores;
  same span.
* ``localdata/statarea.csv.gz`` — probabilities (+HT probs); final scores;
  2017-01-01 → 2026-06-12.

All three archives stop at 2026-06-12 (the sources went historical-only on
that date — see docs/operator/FEATURE-AUDIT-2026-10-10.md). The experiment is
therefore a DEEP-HISTORY study; live-era validation on named-book prices is a
separate, quota-bounded exercise.

Splits (frozen, no tuning against the final test)
-------------------------------------------------
* TRAIN      : date <= 2025-05-31
* VALIDATION : 2025-06-01 → 2025-12-31   (model/calibration selection)
* TEST       : 2026-01-01 → 2026-06-12   (evaluated once per final spec)

Rows are grouped by FIXTURE (date + identity-folded teams); every derived
aggregate (league draw rates, calibration temperatures) is fitted on TRAIN
only and applied unchanged to validation/test.

Baselines and feature groups
----------------------------
* ``market``    — devigged Forebet 1x2 odds (provider-average prices:
                  provenance ``provider_average``, NOT named-book; used as a
                  probability baseline only, never as executable prices).
* ``consensus`` — the source trio's mean probability (temperature-fitted on
                  train).
* ``blend``     — logistic (multinomial) over feature groups, one model per
                  ablation: consensus only / +draw-balance / +market /
                  +forebet extras.

Metrics: multiclass log loss, multiclass Brier, per-outcome calibration
(draws reported explicitly), coverage (n), and per-source vote hit rates for
context. Returns/ROI are deliberately NOT computed here: the deep-history
window has no timestamped named-book prices, and fair/provider-average odds
are not executable. That gate matches the work order ("report returns only
where valid, timestamped executable prices exist").

Usage::

    PYTHONPATH=src python3 scripts/research_beyond_consensus.py \
        [--out research] [--max-rows N]

Outputs
-------
* ``research/beyond_consensus_dataset.csv.gz``   — the fixture-level panel.
* ``research/beyond_consensus_results.json``     — metrics per split/model.
* ``research/beyond_consensus_report.md``        — human-readable summary.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.identity import canonical_league_key, source_team_key  # noqa: E402

LOCALDATA = ROOT / "localdata"

TRAIN_END = "2025-05-31"
VALID_END = "2025-12-31"
TEST_END = "2026-06-12"          # last day the prediction archives cover

SPLITS = {
    "train": (None, TRAIN_END),
    "validation": (TRAIN_END, VALID_END),
    "test": (VALID_END, TEST_END),
}


def _norm_pct(col: pd.Series) -> pd.Series:
    """Percentages (0-100) to probabilities (0-1); values <=1.5 pass through."""
    num = pd.to_numeric(col, errors="coerce")
    return np.where(num > 1.5, num / 100.0, num)


def _devig(o1: pd.Series, ox: pd.Series, o2: pd.Series):
    """Implied probabilities from decimal odds, overround-normalised."""
    a, b, c = (pd.to_numeric(s, errors="coerce") for s in (o1, ox, o2))
    valid = (a > 1.01) & (b > 1.01) & (c > 1.01)
    inv1, invx, inv2 = 1.0 / a, 1.0 / b, 1.0 / c
    over = inv1 + invx + inv2
    return (
        inv1 / over, invx / over, inv2 / over,
        over.where(valid),
        valid,
    )


def _outcome(hs: pd.Series, gs: pd.Series) -> pd.Series:
    h = pd.to_numeric(hs, errors="coerce")
    g = pd.to_numeric(gs, errors="coerce")
    return np.where(h > g, "home", np.where(h == g, "draw", np.where(h < g, "away", None)))


def _fixture_key(df: pd.DataFrame) -> pd.Series:
    return (
        df["date"].astype(str)
        + "|"
        + df["home"].map(source_team_key)
        + "|"
        + df["away"].map(source_team_key)
    )


def load_source(name: str) -> pd.DataFrame:
    path = LOCALDATA / f"{name}.csv.gz"
    df = pd.read_csv(path, low_memory=False)
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["date", "home", "away"])
    for c in ("p1", "px", "p2"):
        df[c] = _norm_pct(df[c])
    df["outcome"] = _outcome(df["hs"], df["gs"])
    df = df[df["outcome"].notna()]
    df["key"] = _fixture_key(df)
    df["league_fold"] = df["league"].map(canonical_league_key)
    return df


def build_panel(max_rows: int | None = None) -> pd.DataFrame:
    """One row per fixture with the trio's probabilities + market baseline."""
    t0 = time.time()
    fb = load_source("forebet")
    zb = load_source("zulubet")
    sa = load_source("statarea")
    print(f"loaded forebet={len(fb):,} zulubet={len(zb):,} statarea={len(sa):,} "
          f"({time.time()-t0:.1f}s)", file=sys.stderr)

    # Fixture identity across sources: same date + identity-folded team pair.
    # Where a source lists the same fixture twice (cups / re-dates), keep a
    # deterministic single row (first in date+key order) BEFORE joining so no
    # fixture can straddle rows.
    def dedupe(df: pd.DataFrame) -> pd.DataFrame:
        return df.sort_values(["date", "key"]).drop_duplicates("key", keep="first")

    fb, zb, sa = dedupe(fb), dedupe(zb), dedupe(sa)

    panel = fb[[
        "date", "key", "league_fold", "home", "away", "outcome",
        "p1", "px", "p2", "odd1", "oddx", "odd2",
        "goalsavg", "pred_hs", "pred_gs", "p_over", "p_under", "p_gg", "p_ng",
    ]].rename(columns={
        "p1": "fb_home", "px": "fb_draw", "p2": "fb_away",
        "odd1": "fb_odd1", "oddx": "fb_oddx", "odd2": "fb_odd2",
        "p_over": "fb_p_over", "p_under": "fb_p_under",
        "p_gg": "fb_p_gg", "p_ng": "fb_p_ng",
    })
    panel = panel.merge(
        zb[["key", "p1", "px", "p2"]].rename(
            columns={"p1": "zb_home", "px": "zb_draw", "p2": "zb_away"}),
        on="key", how="inner",
    ).merge(
        sa[["key", "p1", "px", "p2"]].rename(
            columns={"p1": "sa_home", "px": "sa_draw", "p2": "sa_away"}),
        on="key", how="inner",
    )
    # All three sources present, probabilities sane, outcome known.
    for src in ("fb", "zb", "sa"):
        trio = panel[[f"{src}_home", f"{src}_draw", f"{src}_away"]].to_numpy(float)
        ok = np.isfinite(trio).all(axis=1) & ((trio > 0.01) & (trio < 0.999)).all(axis=1)
        panel = panel[ok]
    panel = panel.drop_duplicates("key")
    if max_rows:
        panel = panel.head(max_rows)
    print(f"panel fixtures (trio complete): {len(panel):,}", file=sys.stderr)

    # --- feature groups (as-of-capture availability only) ----------------
    probs = panel[["fb_home", "fb_draw", "fb_away",
                   "zb_home", "zb_draw", "zb_away",
                   "sa_home", "sa_draw", "sa_away"]].to_numpy(float).reshape(-1, 3, 3)
    panel["avg_home"] = probs[:, :, 0].mean(axis=1)
    panel["avg_draw"] = probs[:, :, 1].mean(axis=1)
    panel["avg_away"] = probs[:, :, 2].mean(axis=1)
    panel["avg_p_maxsel"] = panel[["avg_home", "avg_draw", "avg_away"]].max(axis=1)
    panel["std_p"] = probs.std(axis=1).max(axis=1)          # source disagreement
    panel["draw_spread"] = probs[:, :, 1].max(axis=1) - probs[:, :, 1].min(axis=1)
    panel["strength_balance"] = panel["avg_home"] - panel["avg_away"]

    m1, mx, m2, over, valid = _devig(panel["fb_odd1"], panel["fb_oddx"], panel["fb_odd2"])
    panel["mkt_home"], panel["mkt_draw"], panel["mkt_away"] = m1, mx, m2
    panel["mkt_overround"] = over
    panel["mkt_valid"] = valid.fillna(False)
    # consensus trio pick + agreement (context, not a fitted feature)
    sel = panel[["avg_home", "avg_draw", "avg_away"]].to_numpy(float)
    panel["consensus_pick"] = np.array(["home", "draw", "away"])[sel.argmax(axis=1)]
    panel["consensus_hit"] = (panel["consensus_pick"] == panel["outcome"]).astype(int)
    return panel


def add_train_fit_league_rates(panel: pd.DataFrame) -> pd.DataFrame:
    """League draw/home rates fitted on TRAIN rows only, applied everywhere."""
    train = panel[panel["date"] <= TRAIN_END]
    rates = train.groupby("league_fold").agg(
        lg_draw_rate=("outcome", lambda s: (s == "draw").mean()),
        lg_home_rate=("outcome", lambda s: (s == "home").mean()),
        lg_n=("outcome", "size"),
    ).reset_index()
    # Shrink small leagues toward the global train rates (empirical Bayes).
    k = 50.0
    glob_draw = (train["outcome"] == "draw").mean()
    glob_home = (train["outcome"] == "home").mean()
    rates["lg_draw_rate"] = (
        (rates["lg_n"] * rates["lg_draw_rate"] + k * glob_draw) / (rates["lg_n"] + k))
    rates["lg_home_rate"] = (
        (rates["lg_n"] * rates["lg_home_rate"] + k * glob_home) / (rates["lg_n"] + k))
    return panel.merge(rates[["league_fold", "lg_draw_rate", "lg_home_rate"]],
                       on="league_fold", how="left").fillna(
        {"lg_draw_rate": glob_draw, "lg_home_rate": glob_home})


FEATURE_GROUPS: dict[str, list[str]] = {
    "consensus": ["avg_home", "avg_draw", "avg_away", "std_p", "draw_spread"],
    "balance": ["strength_balance", "avg_draw", "lg_draw_rate", "lg_home_rate"],
    "market": ["mkt_home", "mkt_draw", "mkt_away"],
    "forebet_extras": ["goalsavg", "fb_p_over", "fb_p_under", "fb_p_gg", "fb_p_ng",
                       "fb_extras_missing"],
}


def impute_extras(panel: pd.DataFrame) -> pd.DataFrame:
    """Train-median imputation for Forebet extras + an explicit missing flag.

    Missingness is information (the mission says so), so the imputed columns
    are accompanied by a count of what was missing — fitted nowhere, observed
    at capture.
    """
    extras = ["goalsavg", "fb_p_over", "fb_p_under", "fb_p_gg", "fb_p_ng"]
    train_mask = panel["date"] <= TRAIN_END
    medians = panel.loc[train_mask, extras].median(numeric_only=True)
    panel["fb_extras_missing"] = panel[extras].isna().sum(axis=1).astype(float)
    for col in extras:
        panel[col] = panel[col].fillna(medians.get(col, 0.0))
    return panel

ABLATIONS: dict[str, list[str]] = {
    "consensus_only": ["consensus"],
    "consensus+balance": ["consensus", "balance"],
    "consensus+market": ["consensus", "market"],
    "consensus+market+balance": ["consensus", "market", "balance"],
    "consensus+market+balance+extras": ["consensus", "market", "balance", "forebet_extras"],
}

CLASSES = ("home", "draw", "away")

# Columns that encode the target or outcome-conditioned context. They may sit
# in the dataset for inspection, but must never enter a design matrix.
FORBIDDEN_FEATURES = {
    "outcome", "consensus_pick", "consensus_hit", "pred_hs", "pred_gs",
    "mkt_overround", "hs", "gs",
}

DATASET_SCHEMA: dict[str, str] = {
    "date": "fixture date YYYY-MM-DD (kickoff day, source-published)",
    "key": "date|source_team_key(home)|source_team_key(away) — fixture identity",
    "league_fold": "canonical_league_key(league) — identity-folded competition",
    "home": "forebet home name (raw)",
    "away": "forebet away name (raw)",
    "outcome": "target: home/draw/away from FINAL score (post-match, never a feature)",
    "fb_home/fb_draw/fb_away": "forebet 1x2 probabilities (0-1, prematch)",
    "fb_odd1/fb_oddx/fb_odd2": "forebet provider-average 1x2 decimal odds (NOT executable)",
    "goalsavg": "forebet prematch expected total goals (provider estimate)",
    "pred_hs/pred_gs": "forebet prematch PREDICTED score (context only, excluded from features)",
    "fb_p_over/fb_p_under": "forebet prematch over/under 2.5 probabilities",
    "fb_p_gg/fb_p_ng": "forebet prematch both-teams-score / not probabilities",
    "zb_home/zb_draw/zb_away": "zulubet 1x2 probabilities (0-1, prematch)",
    "sa_home/sa_draw/sa_away": "statarea 1x2 probabilities (0-1, prematch)",
    "avg_home/avg_draw/avg_away": "trio mean probabilities",
    "avg_p_maxsel": "max of trio means (context)",
    "std_p": "max over outcomes of per-outcome std across the trio (disagreement)",
    "draw_spread": "max-min draw probability across the trio",
    "strength_balance": "avg_home - avg_away",
    "mkt_home/mkt_draw/mkt_away": "devigged forebet odds (market baseline; provider-average)",
    "mkt_overround": "book sum of 1/odds before devig (context)",
    "mkt_valid": "True where all three odds > 1.01 (market baseline coverage)",
    "consensus_pick": "argmax trio mean (context, outcome-conditioned hit in consensus_hit)",
    "consensus_hit": "consensus_pick == outcome (context only)",
    "fb_extras_missing": "count of missing forebet extras before imputation (0-5)",
    "lg_draw_rate/lg_home_rate": "league outcome rates, TRAIN rows only, EB shrinkage k=50",
}


def _sha256_bytes(data: bytes) -> str:
    import hashlib
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _leakage_guards(panel: pd.DataFrame, frames: dict[str, pd.DataFrame]) -> None:
    """Machine-checked anti-leakage contract; abort the run on violation."""
    # 1. every feature column of every ablation is allowed
    used = {c for cols in FEATURE_GROUPS.values() for c in cols}
    bad = used & FORBIDDEN_FEATURES
    assert not bad, f"forbidden columns in feature groups: {bad}"
    assert used <= set(panel.columns), f"missing feature columns: {used - set(panel.columns)}"
    # 2. chronological, disjoint splits on fixture keys
    tr, va, te = frames["train"], frames["validation"], frames["test"]
    assert tr["date"].max() <= TRAIN_END and va["date"].min() > TRAIN_END
    assert va["date"].max() <= VALID_END and te["date"].min() > VALID_END
    assert te["date"].max() <= TEST_END
    ktr, kva, kte = set(tr["key"]), set(va["key"]), set(te["key"])
    assert not (ktr & kva) and not (ktr & kte) and not (kva & kte), "fixture straddles splits"
    assert len(panel) == len(ktr) + len(kva) + len(kte)
    # 3. targets are valid classes
    assert set(panel["outcome"]) <= set(CLASSES)
    # 4. train-fitted league rates exist for every row and are finite
    assert panel[["lg_draw_rate", "lg_home_rate"]].notna().all().all()
    assert np.isfinite(panel[["lg_draw_rate", "lg_home_rate"]].to_numpy(float)).all()


def _proba_to_matrix(p: pd.DataFrame) -> np.ndarray:
    return p[["p_home", "p_draw", "p_away"]].to_numpy(float)


def _logloss(y: np.ndarray, P: np.ndarray) -> float:
    idx = np.array([CLASSES.index(v) for v in y])
    return float(-np.log(np.clip(P[np.arange(len(y)), idx], 1e-12, 1)).mean())


def _brier_multi(y: np.ndarray, P: np.ndarray) -> float:
    Y = np.zeros_like(P)
    for i, v in enumerate(y):
        Y[i, CLASSES.index(v)] = 1.0
    return float(((P - Y) ** 2).sum(axis=1).mean())


def _temperature_scale(logits: np.ndarray, y: np.ndarray) -> float:
    """1-d temperature fitted by golden-section on validation log loss."""
    def loss(T: float) -> float:
        Z = logits / T
        Z = Z - Z.max(axis=1, keepdims=True)
        Q = np.exp(Z)
        Q /= Q.sum(axis=1, keepdims=True)
        return _logloss(y, Q)

    lo, hi = 0.25, 8.0
    for _ in range(60):
        m1 = lo + (hi - lo) / 3
        m2 = hi - (hi - lo) / 3
        if loss(m1) < loss(m2):
            hi = m2
        else:
            lo = m1
    return (lo + hi) / 2


def _softmax(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    Z = logits / T
    Z = Z - Z.max(axis=1, keepdims=True)
    Q = np.exp(Z)
    return Q / Q.sum(axis=1, keepdims=True)


def _eval_rows(y: np.ndarray, P: np.ndarray) -> dict:
    """Metric block shared by baselines and ablations."""
    row = {
        "n": int(len(y)),
        "logloss": round(_logloss(y, P), 5),
        "brier_multi": round(_brier_multi(y, P), 5),
        "accuracy": round(float((P.argmax(axis=1) == [CLASSES.index(v) for v in y]).mean()), 4),
    }
    for ci, cls in enumerate(CLASSES):
        mask = y == cls
        row[f"mean_p_when_{cls}"] = round(float(P[mask, ci].mean()), 4) if mask.any() else None
        row[f"rate_{cls}"] = round(float(mask.mean()), 4)
    return row


def _per_row_logloss(y: np.ndarray, P: np.ndarray) -> np.ndarray:
    idx = np.array([CLASSES.index(v) for v in y])
    return -np.log(np.clip(P[np.arange(len(y)), idx], 1e-12, 1))


def _paired_delta_ci(y_a: np.ndarray, P_a: np.ndarray, y_b: np.ndarray,
                     P_b: np.ndarray, dates: np.ndarray, n_boot: int = 2000,
                     seed: int = 42) -> dict:
    """Date-clustered bootstrap CI for logloss(A) - logloss(B).

    Resampling units are CALENDAR DAYS, not fixtures: same-day outcomes share
    conditions, so a fixture-level bootstrap would be anti-conservative. Both
    models are evaluated on identical resampled rows (paired), so the CI
    speaks about the difference, not either model alone.
    """
    assert len(y_a) == len(y_b) and (y_a == y_b).all()
    la, lb = _per_row_logloss(y_a, P_a), _per_row_logloss(y_b, P_b)
    rng = np.random.default_rng(seed)
    uniq = np.unique(dates)
    by_day = {d: np.flatnonzero(dates == d) for d in uniq}
    deltas = np.empty(n_boot)
    for b in range(n_boot):
        days = rng.choice(uniq, size=len(uniq), replace=True)
        idx = np.concatenate([by_day[d] for d in days])
        deltas[b] = la[idx].mean() - lb[idx].mean()
    return {
        "delta_mean": round(float(deltas.mean()), 5),
        "ci95": [round(float(np.percentile(deltas, 2.5)), 5),
                 round(float(np.percentile(deltas, 97.5)), 5)],
        "resample_unit": "calendar_day",
        "n_days": int(len(uniq)),
        "n_boot": n_boot,
    }


def _fit(name: str, X_cols: list[str], train: pd.DataFrame, valid: pd.DataFrame,
         test: pd.DataFrame) -> tuple[dict, np.ndarray, np.ndarray]:
    """One multinomial logistic model + train-fitted temperature."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    Xtr = train[X_cols].to_numpy(float)
    Xva = valid[X_cols].to_numpy(float)
    Xte = test[X_cols].to_numpy(float)
    # Hard guard: the first run crashed here on NaN market/extras columns.
    # Imputation upstream must leave no NaN in any design matrix.
    for label, X in (("train", Xtr), ("validation", Xva), ("test", Xte)):
        if not np.isfinite(X).all():
            bad = [c for c, col in zip(X_cols, X.T) if not np.isfinite(col).all()]
            raise ValueError(f"{name}: NaN/inf in {label} design matrix cols={bad}")
    scaler = StandardScaler().fit(Xtr)
    model = LogisticRegression(max_iter=1000, C=1.0, random_state=42)
    model.fit(scaler.transform(Xtr), train["outcome"].to_numpy())

    # sklearn orders classes alphabetically ('away','draw','home'); reorder
    # every column block into the canonical (home, draw, away) order.
    col_order = [list(model.classes_).index(c) for c in CLASSES]

    def logits(X: np.ndarray) -> np.ndarray:
        return model.decision_function(scaler.transform(X))[:, col_order]

    # Temperature is calibrated on the VALIDATION split (labels of the
    # validation window only); the test split is never touched here.
    T = _temperature_scale(logits(Xva), valid["outcome"].to_numpy())
    out = {"model": name, "temperature": round(T, 4), "splits": {}}
    y_test = P_test = None
    for split, frame, X in (("train", train, Xtr), ("validation", valid, Xva),
                            ("test", test, Xte)):
        y = frame["outcome"].to_numpy()
        P = _softmax(logits(X), T)
        out["splits"][split] = _eval_rows(y, P)
        if split == "test":
            y_test, P_test = y, P
    return out, y_test, P_test


def _baseline_market(frame: pd.DataFrame) -> tuple[dict, np.ndarray, np.ndarray]:
    """Devigged Forebet odds — provider-average provenance, no fitting."""
    sub = frame[frame["mkt_valid"]]
    y = sub["outcome"].to_numpy()
    P = sub[["mkt_home", "mkt_draw", "mkt_away"]].to_numpy(float)
    return _eval_rows(y, P), y, P


def _baseline_consensus(frame: pd.DataFrame, T: float | None) -> tuple[dict, np.ndarray, np.ndarray]:
    """Trio mean probabilities; temperature fitted on train, reused as given."""
    y = frame["outcome"].to_numpy()
    Q = frame[["avg_home", "avg_draw", "avg_away"]].to_numpy(float)
    logits = np.log(np.clip(Q, 1e-6, 1))
    P = _softmax(logits, T if T else 1.0)
    return _eval_rows(y, P), y, P


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "research"))
    ap.add_argument("--max-rows", type=int, default=None)
    args = ap.parse_args()
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    panel = build_panel(args.max_rows)
    panel = impute_extras(panel)
    panel = add_train_fit_league_rates(panel)
    panel.to_csv(outdir / "beyond_consensus_dataset.csv.gz", index=False, compression="gzip")

    results: dict = {"splits": SPLITS, "baselines": {}, "ablations": {}}
    frames = {
        "train": panel[panel["date"] <= TRAIN_END],
        "validation": panel[(panel["date"] > TRAIN_END) & (panel["date"] <= VALID_END)],
        "test": panel[(panel["date"] > VALID_END) & (panel["date"] <= TEST_END)],
    }
    _leakage_guards(panel, frames)
    for name, f in frames.items():
        print(f"{name}: {len(f):,} fixtures "
              f"({f['date'].min()} → {f['date'].max()})", file=sys.stderr)

    # --- baselines -------------------------------------------------------
    mkt_by_split = {split: _baseline_market(f) for split, f in frames.items()}
    results["baselines"]["market_provider_average"] = {
        split: row for split, (row, _y, _P) in mkt_by_split.items()}
    # Consensus-baseline temperature is fitted on TRAIN rows only and reused
    # unchanged on validation/test.
    T_cons = _temperature_scale(
        np.log(np.clip(frames["train"][["avg_home", "avg_draw", "avg_away"]]
                       .to_numpy(float), 1e-6, 1)),
        frames["train"]["outcome"].to_numpy())
    results["baselines"]["consensus_mean_temperature"] = {"temperature": round(T_cons, 4)}
    cons_by_split = {
        split: _baseline_consensus(f, T_cons) for split, f in frames.items()}
    results["baselines"]["consensus_mean"] = {
        split: row for split, (row, _y, _P) in cons_by_split.items()}

    # --- ablations -------------------------------------------------------
    for name, groups in ABLATIONS.items():
        cols = [c for g in groups for c in FEATURE_GROUPS[g]]
        assert not (set(cols) & FORBIDDEN_FEATURES)
        if "market" in groups:
            # The market group needs valid three-way odds; restrict every
            # split to market-valid fixtures and say so in the results.
            sub = {k: f[f["mkt_valid"]] for k, f in frames.items()}
            entry, y_test, P_test = _fit(
                name, cols, sub["train"], sub["validation"], sub["test"])
            entry["restricted_to"] = "mkt_valid"
            for split in sub:
                entry["splits"][split]["n"] = int(len(sub[split]))
            _y_mkt, P_mkt = _baseline_market(sub["test"])[1:]
            _y_cons, P_cons = _baseline_consensus(sub["test"], T_cons)[1:]
            entry["test_delta_ci"] = {
                "vs_consensus_mean": _paired_delta_ci(
                    y_test, P_test, _y_cons, P_cons, sub["test"]["date"].to_numpy()),
                "vs_market_provider_average": _paired_delta_ci(
                    y_test, P_test, _y_mkt, P_mkt, sub["test"]["date"].to_numpy()),
            }
        else:
            entry, y_test, P_test = _fit(
                name, cols, frames["train"], frames["validation"], frames["test"])
            _y_cons, P_cons = cons_by_split["test"][1:]
            entry["test_delta_ci"] = {
                "vs_consensus_mean": _paired_delta_ci(
                    y_test, P_test, _y_cons, P_cons, frames["test"]["date"].to_numpy()),
            }
        results["ablations"][name] = entry

    # --- context (descriptive, unfitted): per-source pick hit rates -------
    test = frames["test"]
    context = {"n_test": int(len(test))}
    for src, cols in (("forebet", ("fb_home", "fb_draw", "fb_away")),
                      ("zulubet", ("zb_home", "zb_draw", "zb_away")),
                      ("statarea", ("sa_home", "sa_draw", "sa_away")),
                      ("trio_mean", ("avg_home", "avg_draw", "avg_away"))):
        pick = np.array(CLASSES)[test[list(cols)].to_numpy(float).argmax(axis=1)]
        context[f"{src}_pick_hit_rate"] = round(
            float((pick == test["outcome"].to_numpy()).mean()), 4)
    results["context"] = context

    (outdir / "beyond_consensus_results.json").write_text(json.dumps(results, indent=2))

    # --- report ----------------------------------------------------------
    def _line(label, row):
        return (f"| {label} | {row['n']:,} | {row['logloss']:.4f} | "
                f"{row['brier_multi']:.4f} | {row['accuracy']:.3f} | "
                f"{row.get('mean_p_when_draw') if row.get('mean_p_when_draw') is not None else '—'} "
                f"| {row.get('rate_draw', '—')} |")

    lines = [
        "# Beyond-consensus baselines (offline research)",
        "",
        "Fixture-level panel of the committed prediction archives "
        "(forebet ∩ zulubet ∩ statarea, all three probabilities present, "
        "outcome known). Deep history only: the archives end 2026-06-12.",
        "",
        "No ROI is reported: this window has no timestamped named-book prices, "
        "and Forebet's odds are provider-average, not executable quotes.",
        "",
        "## Splits",
        "",
        "| split | window | fixtures |",
        "| --- | --- | --- |",
    ]
    for split, f in frames.items():
        lines.append(f"| {split} | {f['date'].min()} → {f['date'].max()} | {len(f):,} |")
    for section in ("baselines", "ablations"):
        lines += ["", f"## {section}", "",
                  "| model | n | logloss | brier | acc | mean p when draw | draw rate |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        table = results[section]
        for name, per_split in table.items():
            if name == "consensus_mean_temperature":
                continue
            row = (per_split.get("splits", {}).get("test")
                   or per_split.get("test") or per_split)
            label = name
            lines.append(_line(label, row))

    lines += ["", "## Test-period logloss deltas (date-clustered bootstrap 95% CI)", "",
              "Negative delta = lower log loss than the reference on the same rows.", "",
              "| model | rows | Δ vs consensus_mean | 95% CI | Δ vs market | 95% CI |",
              "| --- | --- | --- | --- | --- | --- |"]
    for name, entry in results["ablations"].items():
        ci = entry.get("test_delta_ci", {})
        d1 = ci.get("vs_consensus_mean", {})
        d2 = ci.get("vs_market_provider_average", {})
        rows_n = entry["splits"]["test"]["n"]
        lines.append(
            f"| {name} | {rows_n:,} | {d1.get('delta_mean', '—')} "
            f"| [{d1.get('ci95', ['—','—'])[0]}, {d1.get('ci95', ['—','—'])[1]}] "
            f"| {d2.get('delta_mean', '—')} "
            f"| [{d2.get('ci95', ['—','—'])[0]}, {d2.get('ci95', ['—','—'])[1]}] |")

    ctx = results.get("context", {})
    if ctx:
        lines += ["", "## Context: test-period pick hit rates (descriptive, unfitted)", "",
                  f"n = {ctx.get('n_test', '—'):,} test fixtures."]
        for src in ("forebet", "zulubet", "statarea", "trio_mean"):
            lines.append(f"- {src}: {ctx.get(f'{src}_pick_hit_rate')}")

    report = "\n".join(lines) + "\n"
    (outdir / "beyond_consensus_report.md").write_text(report)

    # --- manifest: provenance, schema, content hashes --------------------
    import subprocess
    inputs = {}
    for src in ("forebet", "zulubet", "statarea"):
        p = LOCALDATA / f"{src}.csv.gz"
        d = pd.read_csv(p, usecols=["date"], low_memory=False)
        inputs[src] = {
            "path": str(p.relative_to(ROOT)),
            "sha256": _sha256_file(p),
            "rows": int(len(d)),
            "date_min": str(pd.to_datetime(d["date"], errors="coerce").min().date()),
            "date_max": str(pd.to_datetime(d["date"], errors="coerce").max().date()),
        }
    ds_path = outdir / "beyond_consensus_dataset.csv.gz"
    try:
        git_head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
                                  capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        git_head = "unknown"
    manifest = {
        "experiment": "beyond_consensus_baselines",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "command": "PYTHONPATH=src python3 scripts/research_beyond_consensus.py",
        "git_head": git_head,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "reproducibility": (
            "Deterministic given the three committed input archives: the "
            "dataset_content_sha256 below is the hash of the UNCOMPRESSED csv "
            "bytes; the .gz container itself is not byte-reproducible."),
        "inputs": inputs,
        "outputs": {
            "dataset": {
                "path": str(ds_path.relative_to(ROOT)),
                "file_sha256": _sha256_file(ds_path),
                "content_sha256": _sha256_bytes(
                    pd.read_csv(ds_path, low_memory=False).to_csv(index=False).encode()),
                "rows": int(sum(len(f) for f in frames.values())),
            },
            "results_json_sha256": _sha256_file(outdir / "beyond_consensus_results.json"),
            "report_md_sha256": _sha256_file(outdir / "beyond_consensus_report.md"),
        },
        "splits": {k: {"window": SPLITS[k], "fixtures": int(len(f))}
                   for k, f in frames.items()},
        "schema": DATASET_SCHEMA,
    }
    (outdir / "beyond_consensus_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False))
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
