"""ml-fade research checkpoint — frozen cadence, monitoring warnings,
rule-candidate heuristic, reproducible reporting, and CLI behavior.

Contracts pinned here:

  1. Checkpoints fire ONLY on the predeclared conditions (bootstrap /
     monthly / +50 settled fade rows / +30 active days) — never ad-hoc.
  2. Monitoring is visible-but-not-noisy: accrual stalls, price coverage,
     method drift, contract breaches and conflicts warn; normal model refits
     do NOT.
  3. The automatic rule-candidate signal flips only on the frozen gates and
     can never certify or promote anything.
  4. Reports are reproducible (same inputs -> same bytes), always flag the
     research-only nature, and the checkpoint state advances append-only.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from edgefactory.fade import FADE_FAMILY, PARENT_FAMILY  # noqa: E402
from edgefactory import ml_fade_checkpoint as ckpt  # noqa: E402
from edgefactory.ml_fade_research import (  # noqa: E402
    FROZEN_FEATURE_COLS,
    FadeResearchCollector,
    event_key,
    merge_candidates,
    model_key,
    settle_ledger,
)

NOW = "2026-09-21T12:00:00+02:00"
TODAY = date(2026, 9, 21)

FAKE_MODEL = {
    "coef": [0.01] * len(FROZEN_FEATURE_COLS),
    "intercept": 0.0,
    "feature_cols": list(FROZEN_FEATURE_COLS),
}


def _row(family: str, day: str, i: int, *, ml_p: float = 0.62,
         first_seen: str = NOW, status: str = "pending",
         graduation: str | None = None, zb: float | None = 3.50,
         fb: float | None = 3.60, model=FAKE_MODEL) -> dict:
    is_fade = family == FADE_FAMILY
    key = event_key(family, day, f"Home{i}", f"Away{i}")
    return {
        "event_key": key, "family": family, "date": day, "market": "1x2",
        "sport": "soccer", "league": "L", "home": f"Home{i}", "away": f"Away{i}",
        "kickoff": "19:00", "first_seen_at": first_seen, "captured_at": first_seen,
        "last_seen_at": first_seen, "status": status,
        "pick": ("away" if is_fade else "home"),
        "ml_p": (1 - ml_p) if is_fade else ml_p,
        "avg_p": round(((1 - ml_p) if is_fade else ml_p) * 100, 1),
        "parent_pick": "home" if is_fade else None,
        "parent_ml_p": ml_p if is_fade else None,
        "first_odds_forebet": fb, "first_odds_zulubet": zb,
        "latest_odds_forebet": fb, "latest_odds_zulubet": zb,
        "odds_source": "forebet_best" if fb else None,
        "outcome": "home" if graduation in ("win", "loss") else None,
        "graduation": graduation,
        "score": None, "result_source": None, "settled_at": None,
        "model_key": model_key(model), "model_keys_seen": [model_key(model)],
        "ml_ht_diff": 0.0, "ml_ht_total": 0.0, "repriced_count": 0,
        "settle_notes": [],
    }


def _ledger(rows: list[dict]) -> dict:
    return {"schema": 1, "updated_at": NOW, "rows": rows}


def test_bootstrap_checkpoint_due():
    due, reasons = ckpt.checkpoint_due(ckpt.empty_state(), _ledger([]), today=TODAY)
    assert due and any("bootstrap" in r for r in reasons)


def test_monthly_checkpoint_due():
    state = ckpt.empty_state()
    state["last_eval_at"] = "2026-08-31T20:00:00+02:00"
    due, reasons = ckpt.checkpoint_due(state, _ledger([]), today=date(2026, 9, 1))
    assert due and any("monthly" in r for r in reasons)


def test_not_due_when_nothing_crossed():
    state = ckpt.empty_state()
    state["last_eval_at"] = NOW
    state["last_eval_settled_fade"] = 0
    state["last_eval_active_day"] = TODAY.isoformat()
    due, reasons = ckpt.checkpoint_due(state, _ledger([]), today=TODAY)
    assert not due and reasons == []


def test_settled_increment_checkpoint_due():
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), i, status="settled",
                 graduation="win", first_seen=NOW)
            for i in range(ckpt.SETTLED_INCREMENT)]
    state = ckpt.empty_state()
    state["last_eval_at"] = NOW
    state["last_eval_settled_fade"] = 0
    due, reasons = ckpt.checkpoint_due(state, _ledger(rows), today=TODAY)
    assert due and any("settled fade rows grew" in r for r in reasons)


def test_active_days_checkpoint_due():
    start = TODAY - timedelta(days=ckpt.ACTIVE_DAY_INCREMENT)
    rows = [
        _row(PARENT_FAMILY, (start + timedelta(days=i)).isoformat(), i,
             first_seen=(start + timedelta(days=i)).isoformat() + "T10:00:00+02:00")
        for i in range(ckpt.ACTIVE_DAY_INCREMENT)
    ]
    state = ckpt.empty_state()
    state["last_eval_at"] = start.isoformat() + "T00:00:00+02:00"
    state["last_eval_settled_fade"] = 0
    due, reasons = ckpt.checkpoint_due(state, _ledger(rows), today=TODAY)
    assert due and any("active capture days" in r for r in reasons)


def test_stall_warning_parents_accrue_fades_do_not():
    rows = [_row(PARENT_FAMILY, TODAY.isoformat(), i) for i in range(10)]
    state = ckpt.empty_state()
    state["last_eval_at"] = (TODAY - timedelta(days=7)).isoformat() + "T00:00:00+02:00"
    warnings = ckpt.monitoring_warnings(_ledger(rows), state, FAKE_MODEL,
                                        today=TODAY)
    assert any("FADE ACCRUAL STALL" in w for w in warnings)


def test_no_stall_warning_when_fades_accrue():
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), i) for i in range(3)]
    rows += [_row(PARENT_FAMILY, TODAY.isoformat(), i + 10) for i in range(10)]
    state = ckpt.empty_state()
    state["last_eval_at"] = (TODAY - timedelta(days=7)).isoformat() + "T00:00:00+02:00"
    warnings = ckpt.monitoring_warnings(_ledger(rows), state, FAKE_MODEL,
                                        today=TODAY)
    assert not any("STALL" in w for w in warnings)


def test_price_coverage_warning():
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), i, status="settled",
                 graduation="win", zb=None) for i in range(25)]
    rows += [_row(FADE_FAMILY, TODAY.isoformat(), i + 100, status="settled",
                  graduation="win", zb=3.4) for i in range(10)]
    state = ckpt.empty_state()
    warnings = ckpt.monitoring_warnings(_ledger(rows), state, FAKE_MODEL,
                                        today=TODAY)
    assert any("PRICE COVERAGE LOW (zb-only)" in w for w in warnings)
    # below the minimum settled count -> quiet (no death by a thousand pings)
    few = _ledger(rows[:10])
    quiet = ckpt.monitoring_warnings(few, state, FAKE_MODEL, today=TODAY)
    assert not any("PRICE COVERAGE" in w for w in quiet)


def test_method_drift_and_contract_breach_warnings():
    drifted_model = dict(FAKE_MODEL)
    drifted_model["feature_cols"] = list(reversed(FROZEN_FEATURE_COLS))
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), 0)]
    rows[0]["ml_ht_diff"] = 1.0
    warnings = ckpt.monitoring_warnings(_ledger(rows), ckpt.empty_state(),
                                        drifted_model, today=TODAY)
    assert any("MODEL METHOD DRIFT" in w for w in warnings)
    assert any("CONTRACT BREACH" in w for w in warnings)


def test_normal_refit_is_not_a_warning():
    """Model refits (new coef, same frozen method) stay informational."""
    old_model = dict(FAKE_MODEL)
    refit_model = dict(FAKE_MODEL)
    refit_model["coef"] = [c * 1.1 for c in FAKE_MODEL["coef"]]
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), 0, model=old_model)]
    assert model_key(old_model) != model_key(refit_model)
    warnings = ckpt.monitoring_warnings(_ledger(rows), ckpt.empty_state(),
                                        refit_model, today=TODAY)
    assert warnings == []
    # ...but the turnover is still visible in the drift provenance section
    drift = ckpt.drift_report(_ledger(rows), refit_model)
    assert model_key(old_model) in drift["stale_model_keys"]


def test_conflict_rows_warn():
    rows = [_row(FADE_FAMILY, TODAY.isoformat(), 0, status="conflict")]
    warnings = ckpt.monitoring_warnings(_ledger(rows), ckpt.empty_state(),
                                        FAKE_MODEL, today=TODAY)
    assert any("UNRESOLVED CONFLICTS (ml-fade)" in w for w in warnings)


def _candidate_population(n: int = 200) -> list[dict]:
    rows = []
    for i in range(n):
        # 80% hit at zb 1.9 / fb 1.85 on the fade side: strong but plausible.
        win = i % 5 != 0
        rows.append(_row(FADE_FAMILY, TODAY.isoformat(), i, status="settled",
                         graduation="win" if win else "loss",
                         zb=1.9, fb=1.85))
    return rows


def test_rule_candidate_signal_observing_and_candidate():
    strong = _ledger(_candidate_population())
    assert ckpt.rule_candidate_signal(strong)["status"] == "candidate"

    sparse = _ledger(_candidate_population(100))  # below the settled gate
    sig = ckpt.rule_candidate_signal(sparse)
    assert sig["status"] == "observing"
    assert any("settled fade rows" in r for r in sig["reasons"])

    weak = _ledger([_row(FADE_FAMILY, TODAY.isoformat(), i, status="settled",
                         graduation="win" if i % 2 else "loss", zb=1.4, fb=1.4)
                    for i in range(220)])
    sig2 = ckpt.rule_candidate_signal(weak)
    assert sig2["status"] == "observing"

    # one conflict row blocks the signal (fail closed)
    blocked = _candidate_population()
    blocked[0] = dict(blocked[0], status="conflict", graduation=None)
    sig3 = ckpt.rule_candidate_signal(_ledger(blocked))
    assert sig3["status"] == "observing"
    assert any("conflict" in r for r in sig3["reasons"])


def test_report_render_frozen_banner_and_reproducible():
    ledger = _ledger(_candidate_population(30))
    state = ckpt.empty_state()
    report = ckpt.build_report(ledger, state, FAKE_MODEL, today=TODAY,
                               now=NOW, due_reasons=["bootstrap (test)"])
    md1 = ckpt.render_report_md(report)
    md2 = ckpt.render_report_md(report)
    assert md1 == md2  # reproducibility: same inputs -> same bytes
    assert "FROZEN" in md1 and "RESEARCH-ONLY" in md1
    assert "NOT certification" in md1
    assert "INSUFFICIENT" not in md1  # the checkpoint does not judge the study
    assert "| ml-meta |" in md1 and "| ml-fade |" in md1


def test_apply_checkpoint_advances_state_append_only():
    state = ckpt.empty_state()
    ledger = _ledger(_candidate_population(10))
    report = ckpt.build_report(ledger, state, FAKE_MODEL, today=TODAY, now=NOW,
                               due_reasons=["bootstrap (test)"])
    st1 = ckpt.apply_checkpoint(state, report, now=NOW, report_path="r1.md")
    assert st1["last_eval_at"] == NOW
    assert st1["last_eval_settled_fade"] == 10
    assert len(st1["history"]) == 1
    st2 = ckpt.apply_checkpoint(st1, report, now="2026-10-21T12:00:00+02:00",
                                report_path="r2.md")
    assert len(st2["history"]) == 2
    assert st2["history"][0]["report_file"] == "r1.md"  # earlier entry kept


# ---------------------------------------------------------------------------
# CLI end-to-end on fabricated fixtures (tmp paths; never touches localdata)
# ---------------------------------------------------------------------------

def _cli_env(tmp_path: Path, tmp_ledger: Path) -> dict:
    return {
        "ledger": tmp_ledger,
        "state": tmp_path / "state.json",
        "settled": tmp_path / "settled.json",
        "aliases": tmp_path / "aliases.json",
        "edges": ROOT / "localdata" / "edges_consensus.json",
        "out": tmp_path,
    }


def _run_eval(env: dict, *extra: str) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable, str(ROOT / "scripts" / "ml_fade_research_eval.py"),
        "--today", TODAY.isoformat(),
        "--ledger", str(env["ledger"]), "--state", str(env["state"]),
        "--settled", str(env["settled"]), "--aliases", str(env["aliases"]),
        "--edges", str(env["edges"]), "--out-dir", str(env["out"]),
        "--skip-studies",
        *extra,
    ]
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                          check=False)


def test_cli_settle_checkpoint_and_idempotency(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    cands = []
    for i in range(2):
        c = FadeResearchCollector()
        anchor = {"home": f"Home{i}", "away": f"Away{i}", "league": "L",
                  "sport": "soccer", "kickoff": "19:00"}
        c.record(day=TODAY.isoformat(), anchor=anchor,
                 fb={"odd1": 2.1, "oddx": 3.3, "odd2": 3.6},
                 zb={"odd1": 2.0, "oddx": 3.2, "odd2": 3.5},
                 used=["forebet", "zulubet"], majority_pick="home",
                 ml_p=0.62, z_score=0.5, model=dict(FAKE_MODEL))
        cands.extend(c.finalize())
    ledger = {"schema": 1, "updated_at": None, "rows": []}
    merge_candidates(ledger, cands, now=NOW)
    ledger_path.write_text(json.dumps(ledger))
    (tmp_path / "settled.json").write_text(json.dumps({"schema": 1, "rows": [
        {"date": TODAY.isoformat(), "home": "Home0", "away": "Away0",
         "hs": 2, "gs": 1, "outcome": "home", "src": "forebet_settled"}]}))
    env = _cli_env(tmp_path, ledger_path)

    r1 = _run_eval(env)
    assert r1.returncode == 0, r1.stderr
    assert "checkpoint DUE" in r1.stdout
    assert (tmp_path / f"ml_fade_research_report_{TODAY.isoformat()}.md").exists()
    st1 = json.loads((tmp_path / "state.json").read_text())
    assert st1["eval_count"] == 1 and len(st1["history"]) == 1
    rows_after = json.loads(ledger_path.read_text())["rows"]
    assert sum(1 for r in rows_after if r["status"] == "settled") == 2  # one fixture, both families

    # Second run SAME day: idempotent — no new rows, no second checkpoint.
    r2 = _run_eval(env)
    assert r2.returncode == 0, r2.stderr
    assert "no checkpoint due" in r2.stdout
    st2 = json.loads((tmp_path / "state.json").read_text())
    assert st2["eval_count"] == 1 and len(st2["history"]) == 1
    assert len(json.loads(ledger_path.read_text())["rows"]) == len(rows_after)


def test_cli_intraday_defers_checkpoint_without_consuming(tmp_path):
    """Official-freeze doctrine: intraday runs never evaluate a due
    checkpoint and never consume due-ness; the official run evaluates."""
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(_ledger([])))
    (tmp_path / "settled.json").write_text(json.dumps({"schema": 1, "rows": []}))
    env = _cli_env(tmp_path, ledger_path)

    # Intraday run: bootstrap due-ness exists, but evaluation is deferred.
    r1 = _run_eval(env, "--settle-monitor-only")
    assert r1.returncode == 0, r1.stderr
    assert "DEFERRED to the next official 09:00 SAST freeze" in r1.stdout
    st1 = json.loads((tmp_path / "state.json").read_text())
    assert st1["eval_count"] == 0 and st1["history"] == []
    assert not list(tmp_path.glob("ml_fade_research_report_*.md"))

    # A second intraday run: still deferred (due-ness unconsumed, not reset).
    r2 = _run_eval(env, "--settle-monitor-only")
    assert "DEFERRED" in r2.stdout and json.loads(
        (tmp_path / "state.json").read_text())["eval_count"] == 0

    # The official 09:00 run evaluates the SAME predeclared due-ness.
    r3 = _run_eval(env)
    assert r3.returncode == 0, r3.stderr
    assert "checkpoint DUE (bootstrap" in r3.stdout
    st3 = json.loads((tmp_path / "state.json").read_text())
    assert st3["eval_count"] == 1 and len(st3["history"]) == 1
    assert (tmp_path / f"ml_fade_research_report_{TODAY.isoformat()}.md").exists()


def test_cli_force_checkpoint_overrides_deferral_flag_when_absent(tmp_path):
    """Manual human override work both ways: forced evaluation even when the
    deferral flag is present is still honoured (explicit operator act)."""
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(_ledger([])))
    (tmp_path / "settled.json").write_text(json.dumps({"schema": 1, "rows": []}))
    env = _cli_env(tmp_path, ledger_path)
    r = _run_eval(env, "--settle-monitor-only", "--force-checkpoint")
    assert r.returncode == 0
    assert json.loads((tmp_path / "state.json").read_text())["eval_count"] == 1


def test_daily_cmd_wiring_official_vs_intraday():
    """The pipeline's two autonomous modes must map to the anchor policy:
    official run evaluates; intraday defers via --settle-monitor-only."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import daily

    official = daily.ml_fade_research_cmd("2026-09-21", official_run=True)
    intraday = daily.ml_fade_research_cmd("2026-09-21", official_run=False)
    assert "--settle-monitor-only" not in official
    assert intraday.endswith("--settle-monitor-only")
    assert official.startswith(
        "PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --today 2026-09-21")
    assert intraday.startswith(official)


def test_cli_force_checkpoint_appends_history(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_text(json.dumps(_ledger([])))
    (tmp_path / "settled.json").write_text(json.dumps({"schema": 1, "rows": []}))
    env = _cli_env(tmp_path, ledger_path)
    r1 = _run_eval(env, "--force-checkpoint")
    r2 = _run_eval(env, "--force-checkpoint")
    assert r1.returncode == 0 and r2.returncode == 0
    st = json.loads((tmp_path / "state.json").read_text())
    assert st["eval_count"] == 2 and len(st["history"]) == 2
