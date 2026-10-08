#!/usr/bin/env python3
"""Fit the Phase 5 K-contract candidate model — READ-ONLY.

Why this exists
---------------
The Phase 5 activation gate (`edgefactory.phase5_activation`) admits only a
model whose ``feature_cols`` are exactly the frozen 32-column K contract in
order, with finite coefficients and complete ``era_train_slice_mean``
fallbacks. The legacy trainer in ``scripts/mine_consensus.py`` cannot produce
that shape (its own blocker list says so), so until this script existed the
sanctioned unlock had no fit — meaning a returning feed would have arrived as
*code work plus a retrain*, which is exactly what we do not want twice.

What it reads
-------------
* ``localdata/phase5_shadow/rows.jsonl`` — the forward-era capture (one row
  per source per fixture, ``record_type=phase5_shadow_prediction``).
* ``localdata/warehouse.duckdb`` — donor views (``{source}_settled`` /
  ``{source}``) for whichever sources have committed history.
* ``localdata/settled_results.json`` — outcomes for the shadow era.

The declared sources are read by NAME, with availability flags: a source that
is dark contributes ``_available=0.0`` and its era-train mean. When a feed
returns, this script is re-run unchanged and the same columns come alive.

What it writes
--------------
``localdata/ml_meta_k_candidate.json`` only. Never the operational registry,
never the incumbent baseline, never anything under ``localdata/phase5_*``.

What it refuses
---------------
Below the declared floors (era span, row counts) it writes nothing and prints
the shortfall plus the projected date the floors are met at the observed
accrual rate. Fitting a 32-column model on a few hundred rows would produce a
certificate-shaped artefact that means nothing — the failure mode the era
gates exist to prevent.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sklearn.exceptions import ConvergenceWarning  # noqa: E402

from edgefactory.identity import source_team_key  # noqa: E402
from edgefactory.phase5_activation import DECLARED_SOURCE_ORDER  # noqa: E402
from edgefactory.phase5_activation import K_FEATURES  # noqa: E402
from edgefactory.phase5_k import (  # noqa: E402
    build_k_features,
    default_fallbacks,
    majority_pick,
    payload_problems,
)

DEFAULT_OUT = ROOT / "localdata" / "ml_meta_k_candidate.json"
SHADOW_ROWS = ROOT / "localdata" / "phase5_shadow" / "rows.jsonl"
SETTLED = ROOT / "localdata" / "settled_results.json"
WAREHOUSE = ROOT / "localdata" / "warehouse.duckdb"

# The live election trio (serve elects the pick from these three, in order).
ELECTION_SOURCES = ("forebet", "zulubet", "statarea")
ELECTION_BASE_COLUMNS = {"forebet": "fb_p", "zulubet": "zb_p", "statarea": "sa_p"}
XML_EXTRAS = ("kelly", "pred_hs", "pred_gs", "goalsavg", "p_ng", "p_under", "p_gg")

ERA_VALIDATION_DAYS = 30
ERA_TEST_DAYS = 30
MIN_ERA_TRAIN_ROWS = 2000
MIN_ERA_TRAIN_DAYS = 60
MIN_VALID_ROWS = 300
MIN_TEST_ROWS = 300

_PROB_INDEX = {"home": 0, "draw": 1, "away": 2}


def _top_pick(probs: tuple[float, float, float]) -> str:
    best = max(probs)
    return "home" if best == probs[0] else ("draw" if best == probs[1] else "away")


def _parse_day(value: object) -> date | None:
    text = str(value or "")[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _fixture(store: dict, key: tuple, **fields) -> dict:
    row = store.setdefault(key, {"sources": {}, "outcome": None, "league": None,
                                 "home": None, "away": None, "extras": {}})
    for name, value in fields.items():
        if value is not None:
            row[name] = value
    return row


def _load_settled_outcomes() -> dict:
    """(day, home_key, away_key) -> outcome, via the identity normalizer."""
    out: dict[tuple, str] = {}
    try:
        raw = json.loads(SETTLED.read_text())
    except (OSError, json.JSONDecodeError):
        return out
    for row in raw.get("rows") or []:
        day = str(row.get("date") or "")[:10]
        home, away = row.get("home"), row.get("away")
        outcome = row.get("outcome")
        if not (day and home and away and outcome):
            continue
        out.setdefault((day, source_team_key(home), source_team_key(away)), outcome)
    return out


def load_shadow_fixtures(path: Path, outcomes: dict) -> dict:
    """Forward-era fixtures from the shadow capture (declared sources only)."""
    store: dict = {}
    if not path.exists():
        return store
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("record_type") != "phase5_shadow_prediction":
            continue
        identity = row.get("identity") or {}
        day = str(identity.get("date") or row.get("capture_day") or "")[:10]
        home_key, away_key = identity.get("home_key"), identity.get("away_key")
        source = str(row.get("source") or "")
        probs = row.get("probabilities") or {}
        p1, px, p2 = probs.get("1x2.home"), probs.get("1x2.draw"), probs.get("1x2.away")
        if not (day and home_key and away_key and source) or None in (p1, px, p2):
            continue
        raw_fixture = row.get("raw_fixture") or {}
        entry = _fixture(store, (day, home_key, away_key),
                         home=source_team_key(raw_fixture.get("home")) or None,
                         away=source_team_key(raw_fixture.get("away")) or None,
                         league=row.get("league"))
        entry["sources"][source] = (float(p1), float(px), float(p2))
        entry["outcome"] = entry["outcome"] or outcomes.get(
            (day, home_key, away_key))
    return store


def load_warehouse_fixtures(con, era_start: date, era_end: date) -> dict:
    """Donor-view fixtures inside the era. Sources absent => simply not seen."""
    store: dict = {}
    candidates = list(ELECTION_SOURCES) + [
        s for s in DECLARED_SOURCE_ORDER if s not in ELECTION_SOURCES
    ]
    for source in candidates:
        # Read BOTH the raw table and the settled view. warehouse.py builds
        # "{name}_settled" for the electors as a pure filter - only fixtures
        # with a final score survive - and the forward era is a window of
        # fixtures still to be played, so a settle-only read is blind to
        # exactly the rows the era is made of: the trio reports dark while its
        # feeds are capturing. Neither table is a strict superset (a settled
        # view can carry outcomes a raw shard lacks), so both are read and
        # merged into the same fixture entries.
        names: list[str] = []
        for name in (source, f"{source}_settled"):
            if name in names:
                continue
            try:
                con.execute(f"SELECT 1 FROM {name} LIMIT 0")
            except Exception:
                continue
            names.append(name)
        for table in names:
            cols = {r[1] for r in con.execute(f"PRAGMA table_info('{table}')").fetchall()}
            if not {"p1", "px", "p2"} <= cols:
                continue
            extras = [c for c in ("odd1", "oddx", "odd2", "league", "hs", "gs") + XML_EXTRAS
                      if c in cols]
            select = ", ".join(["date", "home", "away", "p1", "px", "p2"] + extras)
            for row in con.execute(f"SELECT {select} FROM {table}").fetchall():
                rec = dict(zip(["date", "home", "away", "p1", "px", "p2"] + extras, row))
                day = _parse_day(rec["date"])
                if day is None or not (era_start <= day <= era_end):
                    continue
                if rec["home"] is None or rec["away"] is None:
                    continue
                if None in (rec["p1"], rec["px"], rec["p2"]):
                    continue
                home_key, away_key = source_team_key(rec["home"]), source_team_key(rec["away"])
                if not home_key or not away_key:
                    continue
                entry = _fixture(store, (day.isoformat(), home_key, away_key),
                                 league=rec.get("league"))
                entry["sources"][source] = (float(rec["p1"]), float(rec["px"]),
                                            float(rec["p2"]))
                if entry["outcome"] is None and rec.get("hs") is not None \
                        and rec.get("gs") is not None:
                    hs, gs = int(rec["hs"]), int(rec["gs"])
                    entry["outcome"] = "home" if hs > gs else ("away" if hs < gs else "draw")
                for extra in XML_EXTRAS:
                    if rec.get(extra) is not None:
                        entry["extras"].setdefault(extra, float(rec[extra]))
                for col in ("odd1", "oddx", "odd2"):
                    if rec.get(col) is not None:
                        entry["extras"].setdefault(col, float(rec[col]))
    return store


def probe_tables(con, era_start: date, era_end: date) -> dict:
    """Per-source newest-day evidence, for the read-only coverage report.

    Reports every table a source can be read from (raw and settled) so the
    report can separate "the feed is capturing" from "the settled view has not
    caught up yet" without guessing. Read-only: never used by a fit.
    """
    probe: dict = {}
    ordered = list(ELECTION_SOURCES) + [
        s for s in DECLARED_SOURCE_ORDER if s not in ELECTION_SOURCES
    ]
    for source in ordered:
        entry: dict = {}
        for label, table in (("raw", source), ("settled", f"{source}_settled")):
            try:
                overall = con.execute(
                    f"SELECT max(CAST(date AS VARCHAR)) FROM {table} "
                    "WHERE CAST(date AS VARCHAR) LIKE '____-__-__%'"
                ).fetchone()[0]
                in_era = con.execute(
                    f"SELECT count(*) FROM {table} WHERE CAST(date AS VARCHAR) >= ? "
                    "AND CAST(date AS VARCHAR) <= ? AND CAST(date AS VARCHAR) "
                    "LIKE '____-__-__%'",
                    [era_start.isoformat(), era_end.isoformat()],
                ).fetchone()[0]
            except Exception:
                continue
            entry[label] = {"newest": overall, "rows_in_era": int(in_era or 0)}
        # A settled view requires hs, gs AND p1/px/p2 to be present
        # (warehouse.py builds it that way), so its newest day can sit behind
        # the raw table's. Name the cause here rather than leaving a reader to
        # guess between "the results are not in yet" (normal) and "the rows are
        # scored but carry no usable probabilities" (a data fault).
        raw, settled = entry.get("raw"), entry.get("settled")
        if raw and settled and raw.get("newest") and settled.get("newest") \
                and raw["newest"] > settled["newest"]:
            try:
                newer, scored, no_probs = con.execute(
                    f"SELECT count(*), "
                    f"sum(CASE WHEN hs IS NOT NULL AND gs IS NOT NULL THEN 1 ELSE 0 END), "
                    f"sum(CASE WHEN hs IS NOT NULL AND gs IS NOT NULL "
                    f"AND (p1 IS NULL OR px IS NULL OR p2 IS NULL) THEN 1 ELSE 0 END) "
                    f"FROM {source} WHERE CAST(date AS VARCHAR) > ? "
                    "AND CAST(date AS VARCHAR) LIKE '____-__-__%'",
                    [settled["newest"]],
                ).fetchone()
                entry["trailing"] = {
                    "newer_rows": int(newer or 0),
                    "scored": int(scored or 0),
                    "scored_without_probs": int(no_probs or 0),
                }
            except Exception:
                pass
        probe[source] = entry
    return probe


def accrual_text(settled_days) -> str | None:
    """How fast the forward era is filling, printed beside the floors.

    The floors are a distance, not a verdict: reading "0 of 2000 rows" without
    the rate that number is moving at makes a healthy feeding era look broken.
    ``settled_days`` carries one entry per eligible-and-settled fixture (the
    caller applies the eligibility rule, so this never disagrees with the
    ``settled_eligible=`` count printed just above). Returns None — no line —
    when nothing has settled yet; an empty era is already reported and must not
    be dressed up with a rate.
    """
    days = [day for day in settled_days if day]
    if not days:
        return None
    unique = set(days)
    return (f"accrual: {len(days)} settled fixture(s) over {len(unique)} day(s) "
            f"= {len(days) / len(unique):.1f}/day "
            "(a fit is attempted only once the floors below are met)")


def _probe_text(entry: dict | None) -> str:
    """One line-friendly rendering of ``probe_tables`` output for a source."""
    if not entry:
        return "   (no table visible)"
    bits = [f"{label} newest={info['newest']} rows_in_era={info['rows_in_era']}"
            for label, info in (("raw", entry.get("raw")), ("settled", entry.get("settled")))
            if info]
    trailing = entry.get("trailing") or {}
    if trailing.get("newer_rows"):
        scored = trailing.get("scored", 0)
        if not scored:
            why = f"{trailing['newer_rows']} newer row(s) have no final score yet"
        elif trailing.get("scored_without_probs", 0) >= scored:
            why = (f"{scored} newer row(s) are scored but carry no usable p1/px/p2, "
                   "so no settled view can index them")
        else:
            why = (f"{trailing['newer_rows']} newer row(s): {scored} scored, "
                   f"{trailing['scored_without_probs']} of those without probabilities")
        bits.append(f"settled trails raw — {why}")
    return "   " + ("; ".join(bits) if bits else "(no table visible)")


def _merge(*stores: dict) -> dict:
    merged: dict = {}
    for store in stores:
        for key, row in store.items():
            target = _fixture(merged, key)
            target["sources"].update(row.get("sources") or {})
            for field in ("outcome", "league", "home", "away"):
                if row.get(field) is not None and target.get(field) is None:
                    target[field] = row[field]
            for name, value in (row.get("extras") or {}).items():
                target["extras"].setdefault(name, value)
    return merged


def _roll14(frame) -> None:
    """Legacy rolling_hit_rate: trailing 14-day majority-pick hit rate.

    Mirrors the legacy trainer's construction (shift(1) then a 14-day
    rolling window), so day D only ever sees days strictly before D — no
    outcome from the row being scored leaks into its own feature.
    """
    import pandas as pd  # local import keeps the module importable without pandas

    daily = frame.groupby("day").agg(wins=("y", "sum"), total=("y", "count")).reset_index()
    daily["day"] = pd.to_datetime(daily["day"])
    daily = daily.sort_values("day").set_index("day")
    shifted = daily[["wins", "total"]].shift(1)
    rolling = shifted.rolling("14D").sum()
    daily["rolling_hit_rate"] = (rolling["wins"] / rolling["total"]).fillna(0.75)
    mapping = dict(zip(daily.index.date, daily["rolling_hit_rate"]))
    frame["rolling_hit_rate"] = frame["day"].map(mapping).fillna(0.75)


def build_frame(fixtures: dict):
    """Rows -> K base features + target. Sources are carried for the contract."""
    import pandas as pd

    from edgefactory.entities import classify_competition

    records = []
    for (day, home_key, away_key), row in sorted(fixtures.items()):
        sources = row["sources"]
        if row.get("outcome") is None or len(sources) < 2:
            continue
        picks = []
        for source in ELECTION_SOURCES:
            probs = sources.get(source)
            picks.append(_top_pick(probs) if probs else None)
        elected = majority_pick(picks)
        if elected is None:
            continue
        idx = _PROB_INDEX[elected]
        trio = [sources.get(s) for s in ELECTION_SOURCES]
        trio_probs = [p[idx] for p in trio if p]
        source_probs = {
            source: ((sources[source][idx], True) if source in sources else (None, False))
            for source in DECLARED_SOURCE_ORDER
        }
        extras = row.get("extras") or {}
        odds_col = {"home": "odd1", "draw": "oddx", "away": "odd2"}[elected]
        comp = classify_competition(row.get("league"))
        base = {
            "fb_p": sources["forebet"][idx] if "forebet" in sources else None,
            "zb_p": sources["zulubet"][idx] if "zulubet" in sources else None,
            "sa_p": sources["statarea"][idx] if "statarea" in sources else None,
            "avg_p": (sum(trio_probs) / len(trio_probs)) if trio_probs else None,
            "min_p": min(trio_probs) if trio_probs else None,
            "std_p": (sum((v - sum(trio_probs) / len(trio_probs)) ** 2 for v in trio_probs)
                      / len(trio_probs)) ** 0.5 if trio_probs else None,
            "pick_odds": extras.get(odds_col) or 1.5,
            "is_home": 1.0 if elected == "home" else 0.0,
            "is_away": 1.0 if elected == "away" else 0.0,
            "cat_friendly": 1.0 if comp == "friendly" else 0.0,
            "cat_youth": 1.0 if comp == "youth" else 0.0,
            "cat_women": 1.0 if comp == "women" else 0.0,
            "cat_cup": 1.0 if comp == "cup" else 0.0,
            "cat_league": 1.0 if comp == "league" else 0.0,
            "kelly": extras.get("kelly"),
            "pred_total": (extras.get("pred_hs", 0.0) + extras.get("pred_gs", 0.0))
            if extras.get("pred_hs") is not None and extras.get("pred_gs") is not None else None,
            "pred_diff": (extras.get("pred_hs", 0.0) - extras.get("pred_gs", 0.0))
            if extras.get("pred_hs") is not None and extras.get("pred_gs") is not None else None,
            "goalsavg": extras.get("goalsavg"),
            "p_ng": extras.get("p_ng"),
            "p_under": extras.get("p_under"),
            "p_gg": extras.get("p_gg"),
        }
        records.append({
            "day": day,
            "elected": elected,
            "outcome": row["outcome"],
            "source_probs": source_probs,
            "base": base,
        })
    frame = pd.DataFrame.from_records(records)
    if frame.empty:
        return frame
    frame["day"] = pd.to_datetime(frame["day"]).dt.date
    frame["y"] = (frame["elected"] == frame["outcome"]).astype(int)
    _roll14(frame)
    return frame


def era_bounds(frame, *, validation_days: int = ERA_VALIDATION_DAYS,
               test_days: int = ERA_TEST_DAYS) -> dict:
    last = max(frame["day"])
    test_start = last - timedelta(days=test_days - 1)
    valid_start = test_start - timedelta(days=validation_days)
    return {"last": last, "test_start": test_start, "valid_start": valid_start}


def fit_candidate(frame, bounds) -> dict:
    import numpy as np
    from sklearn.linear_model import LogisticRegression

    train = frame[frame["day"] < bounds["valid_start"]]
    valid = frame[(frame["day"] >= bounds["valid_start"]) & (frame["day"] < bounds["test_start"])]
    test = frame[frame["day"] >= bounds["test_start"]]

    def base_of(row) -> dict:
        base = dict(row["base"])
        base["rolling_hit_rate"] = row.get("rolling_hit_rate")
        return base

    # era-train-slice means, present values only; dark columns keep the
    # documented neutral so the artefact stays finite and honest. Presence is
    # tracked from the RAW inputs, never from the imputed vector — otherwise a
    # dark feed would look "live" because its fallback value is finite.
    means = default_fallbacks()
    present: dict[str, list[float]] = {col: [] for col in K_FEATURES}
    for _, row in train.iterrows():
        base = base_of(row)
        for col, value in base.items():
            if col in present and value is not None:
                present[col].append(float(value))
        for source, (prob, is_present) in row["source_probs"].items():
            col = f"{source}_p"
            if col not in present:
                continue
            if is_present and prob is not None:
                present[col].append(float(prob))
                present[f"{source}_available"].append(1.0)
            else:
                present[f"{source}_available"].append(0.0)
    for col, values in present.items():
        if values:
            means[col] = float(sum(values) / len(values))

    def matrix(split):
        rows = []
        for _, row in split.iterrows():
            rows.append(build_k_features(base=base_of(row), sources=row["source_probs"],
                                         fallbacks=means))
        return np.asarray([[r[c] for c in means] for r in rows], dtype=float), rows

    x_train, _ = matrix(train)
    model = LogisticRegression(max_iter=5000, random_state=42)
    converged = True
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        model.fit(x_train, train["y"].to_numpy())
        converged = not any(
            issubclass(w.category, ConvergenceWarning) for w in caught
        )

    metrics = {}
    for name, split in (("train", train), ("validation", valid), ("test", test)):
        if split.empty:
            metrics[name] = {"n": 0}
            continue
        x, _ = matrix(split)
        p = model.predict_proba(x)[:, 1]
        y = split["y"].to_numpy()
        metrics[name] = {
            "n": int(len(y)),
            "hit": round(float((p >= 0.5).astype(int).__eq__(y).mean()), 4),
            "brier": round(float(((p - y) ** 2).mean()), 4),
            "logloss": round(float(-(y * np.log(np.clip(p, 1e-9, 1))
                                    + (1 - y) * np.log(np.clip(1 - p, 1e-9, 1))).mean()), 4),
            "mean_p": round(float(p.mean()), 4),
        }

    coverage = {}
    coefficients = {col: float(c) for col, c in zip(means, model.coef_[0])}
    # The election trio has base columns (fb_p/zb_p/sa_p) rather than source
    # pairs, but its availability matters just as much — report both.
    tracked = list(ELECTION_SOURCES) + [
        source for source in DECLARED_SOURCE_ORDER
        if source not in ELECTION_SOURCES
    ]
    for source in tracked:
        # The trio lives in the base columns (fb_p/zb_p/sa_p); the declared
        # capture sources in {source}_p pairs.
        col = ELECTION_BASE_COLUMNS.get(source, f"{source}_p")
        values = present.get(col, [])
        coverage[source] = {
            "era_train_rows_present": len(values),
            "era_train_rows": int(len(train)),
            "share": round(len(values) / len(train), 4) if len(train) else 0.0,
            "coefficient": round(coefficients.get(col, 0.0), 4),
            "status": "live" if values else "dark",
        }

    payload = {
        "feature_cols": list(means),
        "coef": [coefficients[c] for c in means],
        "intercept": float(model.intercept_[0]),
    }
    return {
        "candidate_model_payload": payload,
        "fallback_method": "era_train_slice_mean",
        "fallback_means": {c: float(means[c]) for c in means},
        "fallback_columns_imputed": sorted(
            c for c, v in present.items() if not v),
        "source_coverage": coverage,
        "metrics": metrics,
        "converged": converged,
        "era": {
            "train": [str(min(train["day"])) if not train.empty else None,
                      str(max(train["day"])) if not train.empty else None],
            "validation": [str(bounds["valid_start"]), str(bounds["test_start"] - timedelta(days=1))],
            "test": [str(bounds["test_start"]), str(bounds["last"])],
        },
        "row_counts": {"train": int(len(train)), "validation": int(len(valid)),
                       "test": int(len(test))},
    }


def _shortfall(frame, bounds) -> list[str]:
    notes = []
    train = frame[frame["day"] < bounds["valid_start"]]
    valid = frame[(frame["day"] >= bounds["valid_start"]) & (frame["day"] < bounds["test_start"])]
    test = frame[frame["day"] >= bounds["test_start"]]
    span = (max(frame["day"]) - min(frame["day"])).days if not frame.empty else 0
    if len(train) < MIN_ERA_TRAIN_ROWS:
        notes.append(f"era-train rows {len(train)} < {MIN_ERA_TRAIN_ROWS}")
    if span < MIN_ERA_TRAIN_DAYS:
        notes.append(f"era span {span}d < {MIN_ERA_TRAIN_DAYS}d")
    if len(valid) < MIN_VALID_ROWS:
        notes.append(f"validation rows {len(valid)} < {MIN_VALID_ROWS}")
    if len(test) < MIN_TEST_ROWS:
        notes.append(f"test rows {len(test)} < {MIN_TEST_ROWS}")
    return notes


def _projected(frame) -> str | None:
    days = sorted({d for d in frame["day"]}) if not frame.empty else []
    if len(days) < 2:
        return None
    per_day = len(frame) / len(days)
    if per_day <= 0:
        return None
    need = math.ceil(MIN_ERA_TRAIN_ROWS / per_day)
    return str(max(days[0] + timedelta(days=need), max(days)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--shadow-rows", type=Path, default=SHADOW_ROWS)
    parser.add_argument("--warehouse", type=Path, default=WAREHOUSE)
    parser.add_argument("--era-start", type=str, default=None,
                        help="first day of the forward era (default: first shadow capture day)")
    parser.add_argument("--explain", action="store_true",
                        help="print coverage and floors without fitting")
    args = parser.parse_args()

    outcomes = _load_settled_outcomes()
    shadow = load_shadow_fixtures(args.shadow_rows, outcomes)
    era_days = sorted({k[0] for k in shadow})
    era_start = (date.fromisoformat(args.era_start) if args.era_start
                 else (date.fromisoformat(era_days[0]) if era_days else None))
    warehouse: dict = {}
    probe: dict = {}
    if args.warehouse.exists() and era_start is not None:
        import duckdb

        con = duckdb.connect(str(args.warehouse), read_only=True)
        try:
            last_day = max(
                [date.fromisoformat(d) for d in era_days] + [era_start]
            )
            warehouse = load_warehouse_fixtures(con, era_start, last_day)
            if args.explain:
                probe = probe_tables(con, era_start, last_day)
        finally:
            con.close()

    fixtures = _merge(shadow, warehouse)
    frame = build_frame(fixtures)

    if args.explain:
        if not args.warehouse.exists():
            print(f"warehouse: missing at {args.warehouse} — only the shadow-captured "
                  "sources can be seen, so no fixture can reach the election trio")
        # Coverage is reported from the RAW fixtures: a fixture only becomes
        # era evidence once it has an outcome AND two sources, so the useful
        # forward-looking number is how much is already captured but unsettled.
        def _eligible(row: dict) -> bool:
            # Same criterion as build_frame: two sources AND at least one of the
            # election trio, whose majority supplies the target.
            return (len(row["sources"]) >= 2
                    and any(src in row["sources"] for src in ELECTION_SOURCES))

        settled = sum(1 for r in fixtures.values()
                      if _eligible(r) and r.get("outcome") is not None)
        pending = sum(1 for r in fixtures.values()
                      if _eligible(r) and r.get("outcome") is None)
        trio_less = sum(1 for r in fixtures.values()
                        if len(r["sources"]) >= 2 and not _eligible(r))
        print(f"era fixtures: settled_eligible={settled} pending_outcome={pending} "
              f"two_source_without_election_trio={trio_less} "
              f"shadow_rows={len(shadow)} warehouse_rows={len(warehouse)} "
              f"shadow_days={len(era_days)}")
        print("  election trio (supplies the target):")
        trio_present = {}
        for source in ELECTION_SOURCES:
            present = sum(1 for row in fixtures.values() if source in row["sources"])
            trio_present[source] = present
            print(f"    {source:16s} fixtures_present={present}{_probe_text(probe.get(source))}")
        print("  declared capture sources (supply the K columns):")
        for source in DECLARED_SOURCE_ORDER:
            present = sum(1 for row in fixtures.values() if source in row["sources"])
            print(f"    {source:16s} fixtures_present={present}{_probe_text(probe.get(source))}")
        if not any(trio_present.values()):
            era_span = (f"{era_days[0]}..{era_days[-1]}" if era_days else "n/a")
            print(
                f"  note: the era window is a window of fixtures still to be played "
                f"({era_span}). fixtures_present counts what each source contributes inside "
                "it, reading that source's raw table AND its settled view. A `raw newest=` "
                "inside the era means the feed is capturing and only the settled table is "
                "behind, because that view keeps fixtures with a final score only; as results "
                "land the same rows enter it on the next warehouse build and the era starts "
                "accruing - no code change and no retrain. Forebet is retired for production "
                "days after 2026-06-12 (source_health.FOREBET_LIVE_LAST_DAY), so the forward "
                "electors are zulubet and statarea."
            )
        accrual = accrual_text(
            day for (day, _h, _a), row in fixtures.items()
            if _eligible(row) and row.get("outcome") is not None
        )
        if accrual:
            print(accrual)
        print(f"floors: era_train_rows={MIN_ERA_TRAIN_ROWS} era_days={MIN_ERA_TRAIN_DAYS} "
              f"valid_rows={MIN_VALID_ROWS} test_rows={MIN_TEST_ROWS}")
        if not frame.empty:
            bounds = era_bounds(frame)
            notes = _shortfall(frame, bounds)
            print("shortfall:", "; ".join(notes) if notes else "none")
            print("projected era-train floor:", _projected(frame))
        return 2 if frame.empty else 0

    if frame.empty:
        print("fit refused: no settled era fixtures with >=2 sources "
              f"(shadow rows={len(shadow)} warehouse rows={len(warehouse)})")
        return 2

    bounds = era_bounds(frame)
    counts = {"fixtures": len(frame), "shadow": len(shadow), "warehouse": len(warehouse),
              "era_start": str(min(frame['day'])), "era_end": str(max(frame['day']))}
    print(json.dumps(counts, sort_keys=True))

    notes = _shortfall(frame, bounds)
    if notes:
        print("fit refused — not enough accrued era data:", "; ".join(notes))
        print("projected era-train floor:", _projected(frame))
        return 3

    result = fit_candidate(frame, bounds)
    problems = payload_problems(
        result["candidate_model_payload"],
        fallback_means=result["fallback_means"],
        require_fallbacks=True,
    )
    if problems:
        print("fit rejected by self-validation:", "; ".join(problems))
        return 4
    if set(result["fallback_means"]) != set(result["candidate_model_payload"]["feature_cols"]):
        print("fit rejected: fallback means do not cover the contract")
        return 4

    artifact = {
        "record_type": "phase5_candidate_model_fit",
        "schema": 1,
        "fitted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "era_start_arg": args.era_start,
        "maps_to_certificate": {
            "candidate_model_payload": "certificate.candidate_model_payload",
            "fallback_means": "certificate.fallback_means",
            "fallback_method": "certificate.fallback_method",
            "source_coverage": "evidence for the era clauses",
        },
        **result,
        "inputs": counts,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(f"wrote {args.out}")
    if not result["converged"]:
        print("WARNING: the fit did not converge — treat this artefact as "
              "diagnostic only until it does")
    print(json.dumps(result["metrics"], sort_keys=True))
    for source, cov in result["source_coverage"].items():
        print(f"  {source:16s} status={cov['status']:5s} share={cov['share']:.3f} "
              f"coef={cov['coefficient']:+.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
