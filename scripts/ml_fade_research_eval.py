#!/usr/bin/env python3
"""ML-fade research maintenance step: settle rows, monitor accrual, run the
frozen checkpoint evaluation when the predeclared cadence says one is due.

RESEARCH-ONLY. This script never touches production surfaces:

  - reads:  the tracked research ledger (written by the capture hook in
    picks_today.py), the tracked settled_results.json facts, the tracked
    team-name aliases, and (read-only) the registry's ml_model payload for
    model-drift provenance;
  - writes: the tracked research ledger (settlement updates only) and the
    tracked checkpoint state, plus the tracked checkpoint report artifacts
    under localdata/ (ml_fade_research_report_*.md, ml_fade_checkpoint_*.txt —
    git-tracked per operator direction 2026-09-21, like the CLV reports);
  - never: edges_consensus.json, picks archives, notifications, auto-tickets,
    or any certification gate.

It does NOT depend on the ignored DuckDB cache: settlement reads only tracked
files. The optional frozen full-population studies (re-run UNMODIFIED at
checkpoints) need the warehouse; if it cannot be materialized they are
skipped with an explicit visible reason — never silently.

Usage:
  PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --today 2026-09-21
  PYTHONPATH=src python3 scripts/ml_fade_research_eval.py --force-checkpoint --skip-studies
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

LOCAL_TZ = ZoneInfo("Africa/Johannesburg")

from edgefactory import ml_fade_checkpoint as ckpt
from edgefactory import ml_fade_research as mfr
from edgefactory.fade import FADE_FAMILY, PARENT_FAMILY

REPORT_PREFIX = "ml_fade_research_report_"
CONTEXTS_OUT_PREFIX = "ml_fade_checkpoint_contexts_"
PRICE_OUT_PREFIX = "ml_fade_checkpoint_price_study_"


def _now_iso() -> str:
    return datetime.now(LOCAL_TZ).isoformat(timespec="seconds")


def _today(today_arg: str | None) -> date:
    if today_arg:
        return date.fromisoformat(today_arg)
    return datetime.now(LOCAL_TZ).date()


def _load_registry_model(edges_path: Path) -> dict | None:
    try:
        data = json.loads(edges_path.read_text())
    except Exception:
        return None
    model = data.get("ml_model")
    return model if isinstance(model, dict) else None


def _load_settled_rows(settled_path: Path) -> list[dict]:
    if not settled_path.exists():
        return []
    try:
        data = json.loads(settled_path.read_text())
        rows = data.get("rows", [])
        return rows if isinstance(rows, list) else []
    except Exception as exc:
        print(
            f"🚨 settled results unreadable at {settled_path}: {exc} — "
            "settling NOTHING this run (fail-closed)",
            file=sys.stderr,
        )
        return []


def _ensure_warehouse(root: Path) -> tuple[bool, str | None]:
    """Materialize the ignored DuckDB cache for the frozen studies, or say why not."""
    wh = root / "localdata" / "warehouse.duckdb"
    if wh.exists():
        return True, None
    try:
        rc = subprocess.run(
            [sys.executable, str(root / "scripts" / "build_warehouse.py")],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        ).returncode
    except Exception as exc:
        return False, f"warehouse build failed to launch: {exc}"
    if rc != 0 or not wh.exists():
        return False, f"warehouse build returned rc={rc}"
    return True, None


def _run_frozen_studies(root: Path, out_dir: Path, today_s: str, timeout: int) -> dict:
    """Re-run the frozen research scripts UNMODIFIED; archive their outputs."""
    ok, why_not = _ensure_warehouse(root)
    if not ok:
        return {"status": "skipped", "reason": why_not}
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs: dict[str, str] = {}
    jobs = (
        (
            "contexts",
            root / "scripts" / "research_ml_fade_contexts.py",
            out_dir / f"{CONTEXTS_OUT_PREFIX}{today_s}.txt",
        ),
        (
            "price_study",
            root / "scripts" / "research_ml_fade_price_study.py",
            out_dir / f"{PRICE_OUT_PREFIX}{today_s}.txt",
        ),
    )
    for name, script, out_path in jobs:
        try:
            env = dict(os.environ)
            env["PYTHONPATH"] = "src"
            result = subprocess.run(
                [sys.executable, str(script)],
                cwd=root,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            payload = result.stdout
            if result.returncode != 0:
                payload += f"\n\n[nonzero rc={result.returncode}]\n" + (result.stderr or "")[-4000:]
            out_path.write_text(payload)
            outputs[name] = str(out_path)
            if result.returncode != 0:
                return {
                    "status": "partial",
                    "reason": f"{name} exited rc={result.returncode} (output archived)",
                    "outputs": outputs,
                }
        except subprocess.TimeoutExpired:
            return {
                "status": "skipped",
                "reason": f"{name} exceeded {timeout}s budget",
                "outputs": outputs,
            }
        except Exception as exc:
            return {"status": "skipped", "reason": f"{name} failed: {exc}", "outputs": outputs}
    return {"status": "archived", "outputs": outputs}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--today", default=None, help="YYYY-MM-DD (default: today SAST)")
    ap.add_argument("--ledger", type=Path, default=ROOT / "localdata" / mfr.LEDGER_NAME)
    ap.add_argument("--state", type=Path, default=ROOT / "localdata" / ckpt.STATE_NAME)
    ap.add_argument("--settled", type=Path, default=ROOT / "localdata" / "settled_results.json")
    ap.add_argument("--aliases", type=Path, default=ROOT / "localdata" / "team_aliases.json")
    ap.add_argument("--edges", type=Path, default=ROOT / "localdata" / "edges_consensus.json")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "localdata")
    ap.add_argument("--force-checkpoint", action="store_true")
    studies = ap.add_mutually_exclusive_group()
    studies.add_argument(
        "--skip-studies",
        action="store_true",
        help="do not re-run the frozen full-population studies",
    )
    studies.add_argument(
        "--with-studies",
        action="store_true",
        help="always attempt frozen studies when a checkpoint runs",
    )
    ap.add_argument("--studies-timeout", type=int, default=1500)
    ap.add_argument(
        "--no-settle", action="store_true", help="capture-only run: skip the settlement pass"
    )
    ap.add_argument(
        "--settle-monitor-only",
        action="store_true",
        help="settle + accrual + monitoring only: if checkpoint conditions "
        "are met, the evaluation is DEFERRED to the official 09:00 SAST "
        "freeze (policy section 3) — due-ness is NOT consumed, the next "
        "official run evaluates. Used by autonomous intraday runs.",
    )
    args = ap.parse_args(argv)

    today = _today(args.today)
    today_s = today.isoformat()
    now = _now_iso()

    registry_model = _load_registry_model(args.edges)
    if registry_model is None:
        print(
            "🚨 registry ml_model unreadable — drift provenance limited "
            "this run (fail-closed note, capture unaffected)",
            file=sys.stderr,
        )

    # ---- 1) settlement pass (idempotent; frozen rows never reopen) --------
    ledger = mfr.load_ledger(args.ledger)
    if not args.no_settle:
        settled_rows = _load_settled_rows(args.settled)
        matcher = mfr.TeamMatcher(mfr.load_alias_groups(args.aliases))
        settle_stats = mfr.settle_ledger(
            ledger, settled_rows, matcher=matcher, now=now, today=today
        )
        mfr.save_ledger(args.ledger, ledger, now=now)
        s = settle_stats.as_dict()
        print(
            f"ml-fade research settle: settled={s['settled']} "
            f"pending={s['still_pending']} unmatched={s['unmatched']} "
            f"conflicts={s['conflicts']} frozen={s['already_frozen']}"
        )
        if s["conflicts"]:
            print(
                f"🚨 settlement conflicts require human review: {s['conflict_keys'][:5]}",
                file=sys.stderr,
            )

    # ---- 2) per-run visibility (every pipeline run, even between checkpoints)
    summary = mfr.family_summary(ledger)
    print(
        "ml-fade research accrual: "
        f"parent rows={summary[PARENT_FAMILY]['rows']} "
        f"(settled {summary[PARENT_FAMILY]['settled']}) | "
        f"fade rows={summary[FADE_FAMILY]['rows']} "
        f"(settled {summary[FADE_FAMILY]['settled']}, "
        f"pending {summary[FADE_FAMILY]['pending']}, "
        f"unmatched {summary[FADE_FAMILY]['unmatched']}, "
        f"conflict {summary[FADE_FAMILY]['conflict']})"
    )

    state = ckpt.load_state(args.state)
    warnings = ckpt.monitoring_warnings(ledger, state, registry_model, today=today)
    for w in warnings:
        print(f"🚨 {w}", file=sys.stderr)

    # ---- 3) checkpoint cadence ---------------------------------------------
    due, reasons = ckpt.checkpoint_due(state, ledger, today=today)
    if args.force_checkpoint:
        due = True
        reasons = reasons or ["forced manual checkpoint"]
    if not due:
        print(
            "ml-fade research: no checkpoint due "
            f"(next: monthly / +{ckpt.SETTLED_INCREMENT} settled fade / "
            f"{ckpt.ACTIVE_DAY_INCREMENT} active days)"
        )
        ckpt.save_state(args.state, state)
        return 0
    if args.settle_monitor_only and not args.force_checkpoint:
        # Official-freeze doctrine (policy section 3, operator direction
        # 2026-09-20): evaluations anchor to the 09:00 SAST official freeze —
        # an explicit manual --force-checkpoint remains the human override.
        # the same cut the auto-bets use. Intraday due-ness is reported but
        # NOT consumed here; state is left untouched so the next official run
        # evaluates with the same predeclared reasons.
        print(
            f"ml-fade research: checkpoint conditions met ({'; '.join(reasons)}) "
            "— evaluation DEFERRED to the next official 09:00 SAST freeze "
            "(settle/monitoring finished normally)"
        )
        ckpt.save_state(args.state, state)
        return 0

    print(f"ml-fade research checkpoint DUE ({'; '.join(reasons)}) — running frozen evaluation")

    studies: dict = {"status": "skipped", "reason": "not requested"}
    if not args.skip_studies:
        studies = _run_frozen_studies(ROOT, args.out_dir, today_s, args.studies_timeout)
        if studies["status"] != "archived":
            print(f"🚨 frozen studies not fully archived: {studies.get('reason')}", file=sys.stderr)

    report = ckpt.build_report(
        ledger, state, registry_model, today=today, now=now, due_reasons=reasons, studies=studies
    )
    md = ckpt.render_report_md(report)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.out_dir / f"{REPORT_PREFIX}{today_s}.md"
    report_path.write_text(md)
    print(f"ml-fade research checkpoint report -> {report_path}")
    print(
        f"ml-fade rule-candidate signal: {report['rule_candidate']['status'].upper()} "
        "(research heuristic — NOT certification)"
    )

    state = ckpt.apply_checkpoint(
        state, report, now=now, report_path=str(report_path), studies=studies
    )
    ckpt.save_state(args.state, state)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
