"""Phase 5 K-contract tests: one builder for fit and serve, feed-ready.

These pin the properties that make a returning feed a DATA event rather than a
code change plus retrain:

* the 32-column contract is assembled in one place, in frozen order;
* a dark source is represented (``_available=0.0`` + era mean), never dropped,
  so the schema does not move when the feed returns;
* the served vector never substitutes a bare ``0.0`` for a missing column;
* a fit produced by ``scripts/fit_phase5_candidate.py`` is accepted by the real
  activation gate's payload validation.
"""
from __future__ import annotations

import importlib.util
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

from edgefactory.phase5_activation import (
    DECLARED_SOURCE_ORDER,
    K_FEATURES,
    _load_passing_certificate,
)
from edgefactory.phase5_k import (
    build_k_features,
    default_fallbacks,
    feature_vector,
    majority_pick,
    payload_problems,
    source_columns,
)

ROOT = Path(__file__).resolve().parent.parent


def _load_script(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# The contract itself
# --------------------------------------------------------------------------
def test_k_row_has_every_column_in_frozen_order():
    row = build_k_features(
        base={"fb_p": 0.6, "zb_p": 0.55, "sa_p": 0.5, "avg_p": 0.55, "is_home": 1.0},
        sources={"zulubet": (0.55, True)},
    )
    assert list(row) == list(K_FEATURES)
    assert set(row) == set(K_FEATURES)
    assert all(isinstance(v, float) for v in row.values())
    assert row["is_home"] == 1.0


def test_dark_source_is_represented_not_dropped():
    row = build_k_features(base={}, sources={}, fallbacks={"forebet_p": 0.42})
    for source in DECLARED_SOURCE_ORDER:
        # the column exists, carries the recorded mean, and says "unavailable"
        assert row[f"{source}_p"] == pytest.approx(
            default_fallbacks()[f"{source}_p"] if source != "forebet" else 0.42
        )
        assert row[f"{source}_available"] == 0.0


def test_source_columns_clamp_and_flag():
    cols = source_columns({"vitibet": (65.0, True), "bzzoiro": (None, False)})
    assert cols["vitibet_p"] == 1.0          # percent feed cannot poison the logit
    assert cols["vitibet_available"] == 1.0
    assert cols["bzzoiro_p"] is None          # dark -> imputed by the builder
    assert cols["bzzoiro_available"] == 0.0


def test_returning_feed_does_not_move_the_schema():
    dark = build_k_features(base={"fb_p": 0.5}, sources={"betclan": (None, False)})
    live = build_k_features(base={"fb_p": 0.5}, sources={"betclan": (0.61, True)})
    assert list(dark) == list(live) == list(K_FEATURES)
    assert dark["betclan_available"] == 0.0 and live["betclan_available"] == 1.0
    assert dark["betclan_p"] != live["betclan_p"]


def test_majority_pick_mirrors_the_engine_rule():
    assert majority_pick(["home", "home", "home"]) == "home"
    assert majority_pick(["away", "away", "home"]) == "away"      # first two agree
    assert majority_pick(["away", "home", "home"]) == "home"      # last two agree
    assert majority_pick(["away", "home", "draw"]) == "away"      # engine fallback: first
    assert majority_pick(["draw", None, None]) == "draw"
    assert majority_pick([None, None, None]) is None


# --------------------------------------------------------------------------
# The served vector must never silently become zeros
# --------------------------------------------------------------------------
def test_feature_vector_imputes_recorded_means_not_zero():
    model = {
        "feature_cols": ["fb_p", "vitibet_p", "vitibet_available"],
        "coef": [1.0, 1.0, 1.0],
        "intercept": 0.0,
        "fallback_means": {"fb_p": 0.5, "vitibet_p": 0.47, "vitibet_available": 0.0},
    }
    vector, imputed = feature_vector({"fb_p": 0.62}, model)
    assert vector == [0.62, 0.47, 0.0]
    assert imputed == ["vitibet_p", "vitibet_available"]


def test_feature_vector_is_identity_when_every_column_is_present():
    model = {
        "feature_cols": ["fb_p", "zb_p"],
        "coef": [1.0, -1.0],
        "intercept": 0.1,
        "fallback_means": {"fb_p": 0.5, "zb_p": 0.5},
    }
    vector, imputed = feature_vector({"fb_p": 0.7, "zb_p": 0.3}, model)
    assert vector == [0.7, 0.3]
    assert imputed == []


# --------------------------------------------------------------------------
# The fit: shape, refusal, and acceptance by the real activation gate
# --------------------------------------------------------------------------
def _synthetic_fixtures(days: int = 200, per_day: int = 25) -> dict:
    rng = random.Random(20261008)
    fixtures: dict = {}
    start = date(2026, 1, 1)
    for offset in range(days):
        day = (start + timedelta(days=offset)).isoformat()
        for slot in range(per_day):
            strength = rng.uniform(0.30, 0.75)
            probs = {}
            for source in ("forebet", "zulubet", "statarea"):
                p = min(0.92, max(0.08, strength + rng.gauss(0, 0.06)))
                probs[source] = (p, 1 - p * 0.9, p * 0.5)
            home_p = max(probs["forebet"][0], probs["zulubet"][0], probs["statarea"][0])
            outcome = "home" if rng.random() < home_p else (
                "draw" if rng.random() < 0.25 else "away")
            key = (day, f"home{slot}", f"away{slot}")
            fixtures[key] = {
                "sources": {s: tuple(probs[s]) for s in probs},
                "outcome": outcome,
                "league": "Test League",
                "extras": {"odd1": 1.8, "oddx": 3.4, "odd2": 4.2},
            }
    return fixtures


def test_fit_payload_is_accepted_by_the_activation_gate(tmp_path):
    module = _load_script("fit_phase5_candidate", "scripts/fit_phase5_candidate.py")
    frame = module.build_frame(_synthetic_fixtures())
    assert len(frame) > module.MIN_ERA_TRAIN_ROWS
    assert module._shortfall(frame, module.era_bounds(frame)) == []

    result = module.fit_candidate(frame, module.era_bounds(frame))
    payload = result["candidate_model_payload"]
    assert payload_problems(
        payload, fallback_means=result["fallback_means"], require_fallbacks=True
    ) == []
    assert set(result["fallback_means"]) == set(K_FEATURES)
    assert result["fallback_method"] == "era_train_slice_mean"
    # The three election sources are live; the five declared capture sources
    # are dark in this fixture, and the artefact says so.
    assert result["source_coverage"]["forebet"]["status"] == "live"
    for source in ("vitibet", "bzzoiro", "betclan", "scoutingstats", "betminer"):
        assert result["source_coverage"][source]["status"] == "dark"
        assert result["source_coverage"][source]["share"] == 0.0

    certificate = {
        "record_type": "phase5_certification_verdict",
        "overall_status": "pass",
        "clauses": {str(i): {"status": "pass"} for i in range(1, 10)},
        "era_id": "era-test",
        "candidate_fit_performed": True,
        "candidate_model_payload": payload,
        "candidate_cuts": [{"rule": "ml-meta avg_p>=55"}],
        "fallback_method": result["fallback_method"],
        "fallback_means": result["fallback_means"],
    }
    path = tmp_path / "certification.json"
    path.write_text(json.dumps(certificate))
    loaded, raw = _load_passing_certificate(path, era_id="era-test")
    assert loaded["candidate_model_payload"]["feature_cols"] == list(K_FEATURES)
    assert raw


def test_fit_refuses_below_the_declared_floors():
    module = _load_script("fit_phase5_candidate_floors", "scripts/fit_phase5_candidate.py")
    frame = module.build_frame(_synthetic_fixtures(days=10, per_day=5))
    notes = module._shortfall(frame, module.era_bounds(frame))
    assert any("era-train rows" in note for note in notes)
    assert any("era span" in note for note in notes)


def test_shadow_capture_parsing_marks_only_present_sources(tmp_path):
    module = _load_script("fit_phase5_candidate_shadow", "scripts/fit_phase5_candidate.py")
    rows = [
        {
            "record_type": "phase5_shadow_prediction",
            "source": "vitibet",
            "capture_day": "2026-10-08",
            "identity": {"date": "2026-10-08", "home_key": "alpha", "away_key": "beta"},
            "probabilities": {"1x2.home": 0.5, "1x2.draw": 0.3, "1x2.away": 0.2},
            "raw_fixture": {"home": "Alpha", "away": "Beta"},
            "league": "Test",
        },
        {
            "record_type": "phase5_shadow_prediction",
            "source": "scoutingstats",
            "capture_day": "2026-10-08",
            "identity": {"date": "2026-10-08", "home_key": "alpha", "away_key": "beta"},
            "probabilities": {"1x2.home": 0.44, "1x2.draw": 0.31, "1x2.away": 0.25},
        },
        {"record_type": "phase5_shadow_attempt", "source": "betclan"},
    ]
    path = tmp_path / "rows.jsonl"
    path.write_text("\n".join(json.dumps(r) for r in rows))
    store = module.load_shadow_fixtures(path, {})
    entry = store[("2026-10-08", "alpha", "beta")]
    assert set(entry["sources"]) == {"vitibet", "scoutingstats"}
    assert entry["sources"]["vitibet"][0] == 0.5


# --------------------------------------------------------------------------
# Warehouse coverage: the era is a window of unplayed fixtures
# --------------------------------------------------------------------------
def _ci_shaped_warehouse(tmp_path):
    """A warehouse shaped like a real run: raw elector tables plus the
    settle-only views ``warehouse.py`` builds for the trio."""
    duckdb = pytest.importorskip("duckdb")
    db = tmp_path / "wh.duckdb"
    con = duckdb.connect(str(db))
    # An elector row for a fixture still to be played (no score yet).
    con.execute(
        "CREATE TABLE zulubet AS SELECT * FROM (VALUES "
        "('2026-10-09', 'Alpha FC', 'Beta FC', 0.51, 0.28, 0.21, NULL, NULL, 'League')) "
        "t(date, home, away, p1, px, p2, hs, gs, league)"
    )
    # Exactly the trio view warehouse.py builds: scored fixtures only.
    con.execute(
        "CREATE VIEW zulubet_settled AS SELECT *, "
        "CASE WHEN hs > gs THEN 'home' WHEN hs < gs THEN 'away' ELSE 'draw' END AS outcome "
        "FROM zulubet WHERE hs IS NOT NULL AND gs IS NOT NULL"
    )
    # A declared source that only exists through a settled table, which is the
    # case vitibet/scoutingstats were built for: outcomes attached by a join.
    con.execute(
        "CREATE TABLE vitibet_settled AS SELECT * FROM (VALUES "
        "('2026-10-09', 'Gamma FC', 'Delta FC', 0.44, 0.31, 0.25, 2, 1, 'League')) "
        "t(date, home, away, p1, px, p2, hs, gs, league)"
    )
    con.close()
    return duckdb, db


def test_warehouse_read_sees_the_raw_row_the_settled_view_drops(tmp_path):
    """The electors' settled views are settle-only; the raw table is the feed.

    A settle-only read reports the trio dark for an entire forward era while
    its feeds are capturing, which is a lie the branch must not tell.
    """
    duckdb, db = _ci_shaped_warehouse(tmp_path)
    module = _load_script("fit_phase5_candidate_raw", "scripts/fit_phase5_candidate.py")
    con = duckdb.connect(str(db), read_only=True)
    try:
        store = module.load_warehouse_fixtures(con, date(2026, 10, 9), date(2026, 10, 9))
    finally:
        con.close()
    rows = list(store.values())
    assert len(rows) == 2, "both the raw elector row and the settled declared row count"
    zulubet = next(r for r in rows if "zulubet" in r["sources"])
    assert zulubet["sources"]["zulubet"] == (0.51, 0.28, 0.21)   # visible, unsettled
    assert zulubet["outcome"] is None                            # and honestly target-less
    vitibet = next(r for r in rows if "vitibet" in r["sources"])
    assert vitibet["outcome"] == "home"                          # settled table still read


def test_probe_separates_a_live_feed_from_a_lagging_settled_view(tmp_path):
    duckdb, db = _ci_shaped_warehouse(tmp_path)
    module = _load_script("fit_phase5_candidate_probe", "scripts/fit_phase5_candidate.py")
    con = duckdb.connect(str(db), read_only=True)
    try:
        probe = module.probe_tables(con, date(2026, 10, 9), date(2026, 10, 15))
    finally:
        con.close()
    assert probe["zulubet"]["raw"]["newest"] == "2026-10-09"
    assert probe["zulubet"]["raw"]["rows_in_era"] == 1
    assert probe["zulubet"]["settled"]["rows_in_era"] == 0
    text = module._probe_text(probe["zulubet"])
    assert "raw newest=2026-10-09" in text
    assert "settled newest=" in text
    assert module._probe_text(None) == "   (no table visible)"


def test_accrual_line_reports_the_rate_the_floors_are_approached_at():
    """The floors without a rate read as a stuck system; the rate is the fix.

    The line must agree with the ``settled_eligible=`` count printed above it
    (same eligibility rule, applied by the caller) and must vanish entirely
    when nothing has settled, so an empty era is never decorated.
    """
    module = _load_script("fit_phase5_candidate_accrual", "scripts/fit_phase5_candidate.py")
    days = ["2026-10-08"] * 14 + ["2026-10-09"] * 6
    text = module.accrual_text(days)
    assert "20 settled fixture(s)" in text
    assert "over 2 day(s) = 10.0/day" in text
    assert "no retrain" not in text            # the note above carries that claim
    assert module.accrual_text([]) is None
    assert module.accrual_text([None, ""]) is None


def _warehouse_with_a_trailing_settled_view(tmp_path, name, newer_row):
    """One scored row on 10-07, then `newer_row` on 10-08, and the trio's
    real settle filter copied from warehouse.py (scores *and* p1/px/p2)."""
    duckdb = pytest.importorskip("duckdb")
    db = tmp_path / f"{name}.duckdb"
    con = duckdb.connect(str(db))
    con.execute(
        "CREATE TABLE zulubet AS SELECT * FROM (VALUES "
        "('2026-10-07', 'Alpha FC', 'Beta FC', 0.51, 0.28, 0.21, 2, 1, 'League')) "
        "t(date, home, away, p1, px, p2, hs, gs, league)"
    )
    con.execute(
        f"INSERT INTO zulubet SELECT * FROM (VALUES {newer_row}) "
        "t(date, home, away, p1, px, p2, hs, gs, league)"
    )
    con.execute(
        "CREATE VIEW zulubet_settled AS SELECT * FROM zulubet "
        "WHERE hs IS NOT NULL AND gs IS NOT NULL "
        "AND p1 IS NOT NULL AND px IS NOT NULL AND p2 IS NOT NULL"
    )
    con.close()
    return duckdb, db


def test_probe_names_why_the_settled_view_trails_the_raw_table(tmp_path):
    """Two causes look identical in `newest=` alone, so the probe states one.

    A row with no final score is normal (results are not in) and resolves on
    the next build; a scored row whose probabilities did not parse never
    settles at all and needs a look at the shard. Reporting only "settled
    newest=..." makes those two indistinguishable.
    """
    module = _load_script("fit_phase5_candidate_trailing", "scripts/fit_phase5_candidate.py")

    duckdb, db = _warehouse_with_a_trailing_settled_view(
        tmp_path, "unscored", "('2026-10-08', 'Gamma FC', 'Delta FC', 0.4, 0.3, 0.3, NULL, NULL, 'League')"
    )
    con = duckdb.connect(str(db), read_only=True)
    try:
        probe = module.probe_tables(con, date(2026, 10, 7), date(2026, 10, 8))
    finally:
        con.close()
    entry = probe["zulubet"]
    assert entry["raw"]["newest"] == "2026-10-08"
    assert entry["settled"]["newest"] == "2026-10-07"
    assert entry["trailing"] == {"newer_rows": 1, "scored": 0, "scored_without_probs": 0}
    assert "no final score yet" in module._probe_text(entry)

    duckdb, db = _warehouse_with_a_trailing_settled_view(
        tmp_path, "noprobs", "('2026-10-08', 'Gamma FC', 'Delta FC', NULL, NULL, NULL, 1, 1, 'League')"
    )
    con = duckdb.connect(str(db), read_only=True)
    try:
        probe = module.probe_tables(con, date(2026, 10, 7), date(2026, 10, 8))
    finally:
        con.close()
    entry = probe["zulubet"]
    assert entry["trailing"] == {"newer_rows": 1, "scored": 1, "scored_without_probs": 1}
    assert "no usable p1/px/p2" in module._probe_text(entry)

    # No trailing rows at all -> no clause invented.
    con = duckdb.connect(":memory:")
    con.execute("CREATE TABLE zulubet (date VARCHAR, home VARCHAR, away VARCHAR, "
                "p1 DOUBLE, px DOUBLE, p2 DOUBLE, hs INT, gs INT)")
    con.execute("INSERT INTO zulubet VALUES ('2026-10-07','A','B',0.5,0.3,0.2,1,0)")
    entry = module.probe_tables(con, date(2026, 10, 7), date(2026, 10, 7))["zulubet"]
    assert "trailing" not in entry
    assert "settled trails raw" not in module._probe_text(entry)
    con.close()


def test_probe_raw_shards_read_only(tmp_path, monkeypatch):
    import duckdb
    import gzip
    module = _load_script("probe_raw_shards", "scripts/fit_phase5_candidate.py")
    monkeypatch.setattr(module, "LOCALDATA", tmp_path)
    with gzip.open(tmp_path / "forebet.csv.gz", "wt") as handle:
        handle.write("date,hs,gs,p1,px,p2\n2026-10-07,1,0,0.6,0.2,0.2\n2026-10-08,,,0.6,0.2,0.2\n")
    db = str(tmp_path / "warehouse.db")
    with duckdb.connect(db) as con:
        con.execute("CREATE TABLE forebet_settled AS SELECT '2026-10-07' AS date")
    with duckdb.connect(db, read_only=True) as con:
        entry = module.probe_tables(con, date(2026, 10, 1), date(2026, 10, 9))["forebet"]
        assert entry["raw"]["newest"] > entry["settled"]["newest"]
        assert entry["trailing"]["newer_rows"] == 1
        assert "no final score yet" in module._probe_text(entry)
    print("P1 after:", entry, module._probe_text(entry))


def test_probe_dark_source_and_table_precedence(tmp_path, monkeypatch):
    import duckdb
    module = _load_script("probe_dark", "scripts/fit_phase5_candidate.py")
    monkeypatch.setattr(module, "LOCALDATA", tmp_path)
    with duckdb.connect() as con:
        assert module._probe_text(module.probe_tables(con, date(2026, 10, 1), date(2026, 10, 9))["betminer"]) == "   (no table visible)"
        con.execute("CREATE TABLE forebet (date VARCHAR)")
        assert module._raw_relation(con, "forebet") == "forebet"
