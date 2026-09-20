"""ML-fade research checkpoint policy + frozen reference evaluation.

PREDECLARED POLICY (frozen 2026-09-20 — do not edit in response to interim
performance; see ML_FADE_RESEARCH_POLICY.md for the change procedure):

Checkpoints are DUE when any of these fixed conditions holds:
  1. BOOTSTRAP: no checkpoint has ever run;
  2. MONTHLY: the calendar month (SAST) has advanced since the last checkpoint;
  3. SETTLED INCREMENT: settled ml-fade rows grew by >= SETTLED_INCREMENT;
  4. ACTIVE DAYS: at least ACTIVE_DAY_INCREMENT distinct capture days passed
     since the last checkpoint.

At a checkpoint the evaluation is FROZEN:
  - the same fixed price variants (zb-only / fb-only on FIRST-seen bet-time
    quotes) are computed for the ml-meta parent and the ml-fade populations;
  - the same frozen reference accumulator slices (avg_p/ parent_ml_p grids
    at 55/60/65/70) are reported;
  - the same automatic rule-candidate gates are applied (see below);
  - the frozen context scan and price study scripts are re-run UNMODIFIED by
    the checkpoint runner (scripts/ml_fade_research_eval.py), whose outputs
    are archived under localdata/ (ignored — research outputs only).

AUTOMATIC RULE-CANDIDATE GATES (research heuristic — NEVER certification):
  fade zb-only: n_priced >= 150 AND wilson_lb >= 0.55 AND roi > 0
  fade fb-only: n_priced >= 150 AND wilson_lb >= 0.55 AND roi > 0
  settled fade rows total >= 200
  AND no unresolved conflict rows in the fade family.
Only when ALL hold does the report print "candidate"; otherwise "observing".
This signal exists so a human notices the evidence has matured. It cannot
certify, promote, or alter any operational system: certification remains the
existing walk-forward machinery with its existing gates, untouched.

MONITORING (always visible, never silent):
  - fade accrual stall: >= MIN_PARENT_ACCRUAL_FOR_STALL_WARN new parent rows
    since the last checkpoint but zero new fade rows;
  - fade price coverage: settled fade >= 30 and first-quote coverage below
    PRICE_COVERAGE_MIN for either book;
  - model drift: serving model feature method differs from the frozen one,
    or rows carry non-zero checkpoint-⑫ contract features;
  - unresolved conflict rows exist.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from edgefactory.fade import FADE_FAMILY, PARENT_FAMILY
from edgefactory.ml_fade_research import (
    SCHEMA,
    accrual_between,
    active_days,
    detect_model_drift,
    family_summary,
    model_key,
    price_stats,
    rows_by_family,
)

STATE_NAME = "ml_fade_research_state.json"

# --- frozen checkpoint cadence (predeclared 2026-09-20) ---------------------
CHECKPOINT_FROZEN_AT = "2026-09-20"
SETTLED_INCREMENT = 50
ACTIVE_DAY_INCREMENT = 30

# --- frozen rule-candidate gates (research heuristic, see module docstring) -
RULE_CANDIDATE_MIN_SETTLED_FADE = 200
RULE_CANDIDATE_MIN_PRICED = 150
RULE_CANDIDATE_MIN_WILSON_LB = 0.55
RULE_CANDIDATE_MIN_ROI = 0.0

# --- frozen monitoring thresholds -------------------------------------------
MIN_PARENT_ACCRUAL_FOR_STALL_WARN = 10
PRICE_COVERAGE_MIN = 0.90
PRICE_COVERAGE_MIN_SETTLED_N = 30

# Frozen reference accumulator grids (fixed slices, both families).
FROZEN_GRIDS = (55.0, 60.0, 65.0, 70.0)

# Fixed price variants: (label, ledger field on FIRST-seen bet-time quotes).
PRICE_VARIANTS = (
    ("zb-only", "first_odds_zulubet"),
    ("fb-only", "first_odds_forebet"),
)


def default_state_path(root: Path) -> Path:
    return root / "localdata" / STATE_NAME


def empty_state() -> dict:
    return {
        "schema": SCHEMA,
        "checkpoint_frozen_at": CHECKPOINT_FROZEN_AT,
        "policy": {
            "monthly": True,
            "settled_increment": SETTLED_INCREMENT,
            "active_day_increment": ACTIVE_DAY_INCREMENT,
            "rule_candidate_gates": {
                "min_settled_fade": RULE_CANDIDATE_MIN_SETTLED_FADE,
                "min_priced_per_book": RULE_CANDIDATE_MIN_PRICED,
                "min_wilson_lb": RULE_CANDIDATE_MIN_WILSON_LB,
                "min_roi": RULE_CANDIDATE_MIN_ROI,
            },
        },
        "last_eval_at": None,
        "last_eval_settled_fade": 0,
        "last_eval_active_day": None,
        "eval_count": 0,
        "history": [],
        "model_drift": None,
    }


def load_state(path: Path | str) -> dict:
    p = Path(path)
    if not p.exists():
        return empty_state()
    data = json.loads(p.read_text())
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError(
            f"research checkpoint state at {p} has unexpected schema — "
            "failing closed (no silent migration)"
        )
    # Tolerate older-but-same-schema states with missing new keys.
    state = empty_state()
    state.update(data)
    return state


def save_state(path: Path | str, state: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")
    tmp.replace(p)


# ---------------------------------------------------------------------------
# Cadence
# ---------------------------------------------------------------------------


def checkpoint_due(state: dict, ledger: dict, *, today: date) -> tuple[bool, list[str]]:
    """Fixed conditions from the predeclared policy; any one is enough."""
    reasons: list[str] = []
    last_eval_at = state.get("last_eval_at")
    if not last_eval_at:
        reasons.append("bootstrap (no checkpoint has ever run)")
    else:
        last_day = str(last_eval_at)[:10]
        if last_day[:7] != today.isoformat()[:7]:
            reasons.append(f"monthly checkpoint (last {last_day[:7]}, now {today.isoformat()[:7]})")
        fade_settled_now = family_summary(ledger)[FADE_FAMILY]["settled"]
        grew = fade_settled_now - int(state.get("last_eval_settled_fade") or 0)
        if grew >= SETTLED_INCREMENT:
            reasons.append(f"settled fade rows grew by {grew} (>= {SETTLED_INCREMENT})")
        days = active_days(ledger, since=last_day)
        if len(days) >= ACTIVE_DAY_INCREMENT:
            reasons.append(
                f"{len(days)} active capture days since last checkpoint (>= {ACTIVE_DAY_INCREMENT})"
            )
    return (bool(reasons), reasons)


# ---------------------------------------------------------------------------
# Evaluation (frozen definitions — deterministic functions of the ledger)
# ---------------------------------------------------------------------------


def _grid_slice(rows: list[dict], family: str, threshold: float) -> list[dict]:
    if family == FADE_FAMILY:
        return [r for r in rows if float(r.get("parent_ml_p") or 0.0) * 100.0 >= threshold]
    return [r for r in rows if float(r.get("ml_p") or 0.0) * 100.0 >= threshold]


def reference_accumulators(ledger: dict) -> list[dict]:
    """Frozen reference slices for both families, both fixed price variants."""
    out: list[dict] = []
    for family in (PARENT_FAMILY, FADE_FAMILY):
        rows = rows_by_family(ledger, family)
        for thr in FROZEN_GRIDS:
            sliced = _grid_slice(rows, family, thr)
            for label, field in PRICE_VARIANTS:
                stats = price_stats(sliced, field)
                out.append(
                    {
                        "family": family,
                        "grid": f"avg_p>={thr:g}"
                        if family == PARENT_FAMILY
                        else f"parent avg_p>={thr:g}",
                        "price_variant": label,
                        "rows": len(sliced),
                        **stats,
                    }
                )
    return out


def rule_candidate_signal(ledger: dict) -> dict:
    """The ONE automatic gate set in the system: a research-visibility flag.

    Returns {status: 'candidate'|'observing', reasons: [...], gates: {...}}.
    """
    fade_rows = rows_by_family(ledger, FADE_FAMILY)
    summary = family_summary(ledger)[FADE_FAMILY]
    gates: dict[str, dict] = {}
    failed: list[str] = []

    zb = price_stats(fade_rows, "first_odds_zulubet")
    fb = price_stats(fade_rows, "first_odds_forebet")
    gates["zb-only"] = zb
    gates["fb-only"] = fb

    total_ok = summary["settled"] >= RULE_CANDIDATE_MIN_SETTLED_FADE
    gates["settled_fade_total"] = {
        "n": summary["settled"],
        "required": RULE_CANDIDATE_MIN_SETTLED_FADE,
        "ok": total_ok,
    }
    if not total_ok:
        failed.append(f"settled fade rows {summary['settled']} < {RULE_CANDIDATE_MIN_SETTLED_FADE}")
    for label, stats in (("zb-only", zb), ("fb-only", fb)):
        if (stats["n_priced"] or 0) < RULE_CANDIDATE_MIN_PRICED:
            failed.append(f"{label} n_priced {stats['n_priced']} < {RULE_CANDIDATE_MIN_PRICED}")
        if stats["wilson_lb"] is None or stats["wilson_lb"] < RULE_CANDIDATE_MIN_WILSON_LB:
            failed.append(
                f"{label} wilson_lb {_fmt(stats['wilson_lb'])} < {RULE_CANDIDATE_MIN_WILSON_LB}"
            )
        if stats["roi"] is None or stats["roi"] <= RULE_CANDIDATE_MIN_ROI:
            failed.append(f"{label} roi {_fmt(stats['roi'])} <= {RULE_CANDIDATE_MIN_ROI}")
    if summary["conflict"]:
        failed.append(f"{summary['conflict']} unresolved conflict row(s) in fade family")

    return {
        "status": "observing" if failed else "candidate",
        "reasons": failed,
        "gates": gates,
        "note": (
            "automatic research heuristic only — certification remains "
            "the existing walk-forward machinery, untouched"
        ),
    }


def drift_report(ledger: dict, registry_model: dict | None) -> dict:
    """Model provenance: current drift vs frozen method + historical turnover."""
    drift = detect_model_drift(registry_model)
    rows = ledger.get("rows", [])
    current = model_key(registry_model)
    other_keys: dict[str, int] = {}
    contract_breaches: list[str] = []
    for r in rows:
        for k in r.get("model_keys_seen") or []:
            if k and k != current:
                other_keys[k] = other_keys.get(k, 0) + 1
        if r.get("ml_ht_diff") or r.get("ml_ht_total"):
            contract_breaches.append(str(r.get("event_key")))
    return {
        "current_model_key": current,
        "method_drifted": drift["drifted"],
        "drift_reasons": drift["reasons"],
        "stale_model_keys": other_keys,
        "contract_breach_rows": contract_breaches,
    }


def monitoring_warnings(
    ledger: dict, state: dict, registry_model: dict | None, *, today: date
) -> list[str]:
    """Visible monitoring lines; empty list means quiet system (healthy)."""
    warnings: list[str] = []
    summary = family_summary(ledger)
    last_day = str(state.get("last_eval_at"))[:10] if state.get("last_eval_at") else None
    today_s = today.isoformat()

    new_parents = accrual_between(ledger, PARENT_FAMILY, last_day, today_s)
    new_fades = accrual_between(ledger, FADE_FAMILY, last_day, today_s)
    if new_parents >= MIN_PARENT_ACCRUAL_FOR_STALL_WARN and new_fades == 0:
        warnings.append(
            f"FADE ACCRUAL STALL: {new_parents} new ml-meta parent rows since "
            f"{last_day or 'ledger start'} but 0 new ml-fade rows — eligible "
            "fixtures are being scored without fade capture"
        )

    fade = summary[FADE_FAMILY]
    fade_rows = rows_by_family(ledger, FADE_FAMILY)
    if fade["settled"] >= PRICE_COVERAGE_MIN_SETTLED_N:
        for label, field in PRICE_VARIANTS:
            cov = price_stats(fade_rows, field)["priced_coverage"]
            if cov is not None and cov < PRICE_COVERAGE_MIN:
                warnings.append(
                    f"FADE PRICE COVERAGE LOW ({label}): {cov:.0%} of settled "
                    f"fade rows carry a first-seen {label} quote "
                    f"(< {PRICE_COVERAGE_MIN:.0%} threshold)"
                )

    drift = drift_report(ledger, registry_model)
    if drift["method_drifted"]:
        warnings.append("MODEL METHOD DRIFT: " + "; ".join(drift["drift_reasons"]))
    # NOTE: model REFIT (new coef under the same frozen serving method) is the
    # pipeline's scheduled behavior — it is recorded as provenance
    # (model_keys_seen / Provenance section) but must never cry wolf: a
    # warning that always fires gets ignored, which is worse than none.
    # Only METHOD drift (feature set/order) is loud.
    if drift["contract_breach_rows"]:
        warnings.append(
            f"CHECKPOINT-⑫ CONTRACT BREACH in {len(drift['contract_breach_rows'])} "
            "research row(s) (non-zero ht_diff/ht_total at capture): "
            + ", ".join(drift["contract_breach_rows"][:5])
            + (" …" if len(drift["contract_breach_rows"]) > 5 else "")
        )
    for family in (PARENT_FAMILY, FADE_FAMILY):
        cf = summary[family]["conflict"]
        if cf:
            warnings.append(
                f"UNRESOLVED CONFLICTS ({family}): {cf} row(s) hold "
                "contradictory result claims — human review required, never "
                "auto-resolved"
            )
    return warnings


def build_report(
    ledger: dict,
    state: dict,
    registry_model: dict | None,
    *,
    today: date,
    now: str,
    due_reasons: list[str] | None = None,
    studies: dict | None = None,
) -> dict:
    """Assemble the full checkpoint report (machine-readable)."""
    summary = family_summary(ledger)
    return {
        "generated_at": now,
        "today": today.isoformat(),
        "checkpoint_frozen_at": CHECKPOINT_FROZEN_AT,
        "due_reasons": list(due_reasons or []),
        "accrual": summary,
        "new_since_last_eval": {
            family: accrual_between(
                ledger,
                family,
                (str(state.get("last_eval_at"))[:10] if state.get("last_eval_at") else None),
                today.isoformat(),
            )
            for family in (PARENT_FAMILY, FADE_FAMILY)
        },
        "price_variants": {
            family: {
                label: price_stats(rows_by_family(ledger, family), field)
                for label, field in PRICE_VARIANTS
            }
            for family in (PARENT_FAMILY, FADE_FAMILY)
        },
        "reference_accumulators": reference_accumulators(ledger),
        "rule_candidate": rule_candidate_signal(ledger),
        "warnings": monitoring_warnings(ledger, state, registry_model, today=today),
        "drift": drift_report(ledger, registry_model),
        "studies": studies or {},
    }


# ---------------------------------------------------------------------------
# Rendering (deterministic: same report dict -> same bytes)
# ---------------------------------------------------------------------------


def _fmt(value: object, pct: bool = False) -> str:
    if value is None:
        return "—"
    try:
        v = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{v:.1%}" if pct else f"{v:.4f}".rstrip("0").rstrip(".")


def render_report_md(report: dict) -> str:
    L: list[str] = []
    a = L.append
    a(f"# ML-Fade Research Checkpoint — {report['today']}")
    a("")
    a(
        "**RESEARCH-ONLY — definitions FROZEN at "
        f"{report['checkpoint_frozen_at']} and never change. "
        "This report cannot certify, promote, or alter any operational pick, "
        "ticket, gate, or registry entry.**"
    )
    a("")
    if report["due_reasons"]:
        a("Checkpoint due because: " + "; ".join(report["due_reasons"]) + ".")
        a("")
    a("## Accrual (cumulative, plus new since last checkpoint)")
    a("")
    a("| family | rows | settled | pending | conflict | unmatched | new |")
    a("|---|---|---|---|---|---|---|")
    for family in (PARENT_FAMILY, FADE_FAMILY):
        acc = report["accrual"][family]
        a(
            f"| {family} | {acc['rows']} | {acc['settled']} | {acc['pending']} "
            f"| {acc['conflict']} | {acc['unmatched']} "
            f"| +{report['new_since_last_eval'][family]} |"
        )
    a("")
    a("## Fixed price variants (first-seen bet-time quotes)")
    for family in (PARENT_FAMILY, FADE_FAMILY):
        a("")
        a(f"### {family}")
        a("")
        a("| variant | settled | wins | hit | Wilson LB | priced | ROI |")
        a("|---|---|---|---|---|---|---|")
        for label, _field in PRICE_VARIANTS:
            s = report["price_variants"][family][label]
            a(
                f"| {label} | {s['n']} | {s['wins']} | {_fmt(s['hit'], pct=True)} "
                f"| {_fmt(s['wilson_lb'], pct=True)} | {s['n_priced']} "
                f"| {_fmt(s['roi'], pct=True)} |"
            )
    a("")
    a("## Reference accumulators (frozen grids — research contexts)")
    a("")
    a("| family | grid | variant | rows | settled | priced | hit | ROI | Wilson LB |")
    a("|---|---|---|---|---|---|---|---|---|")
    for acc in report["reference_accumulators"]:
        a(
            f"| {acc['family']} | {acc['grid']} | {acc['price_variant']} "
            f"| {acc['rows']} | {acc['n']} | {acc['n_priced']} "
            f"| {_fmt(acc['hit'], pct=True)} | {_fmt(acc['roi'], pct=True)} "
            f"| {_fmt(acc['wilson_lb'], pct=True)} |"
        )
    rc = report["rule_candidate"]
    a("")
    a("## Automatic rule-candidate signal (research heuristic — NOT certification)")
    a("")
    a(f"**Status: {rc['status'].upper()}**")
    if rc["reasons"]:
        a("")
        for reason in rc["reasons"]:
            a(f"- unmet gate: {reason}")
    else:
        a("")
        a("- all predeclared gates satisfied on ledger evidence")
    a("")
    a(f"> {rc['note']}.")
    a("")
    a("## Warnings")
    a("")
    if report["warnings"]:
        for w in report["warnings"]:
            a(f"- 🚨 {w}")
    else:
        a("- none — accrual, pricing coverage and model provenance healthy")
    a("")
    a("## Frozen full-population studies")
    a("")
    studies = report.get("studies") or {}
    if studies.get("status") == "archived":
        a(
            "The frozen, unmodified research scripts were re-run at this "
            "checkpoint; outputs archived:"
        )
        for name, path in sorted((studies.get("outputs") or {}).items()):
            a(f"- `{name}` → `{path}`")
    else:
        a(
            f"Frozen studies NOT re-run this checkpoint "
            f"({studies.get('status', 'unknown')}: {studies.get('reason', '')}). "
            "Manual rerun: see ML_FADE_RESEARCH_POLICY.md."
        )
    a("")
    drift = report["drift"]
    a("## Provenance")
    a("")
    a(f"- serving model key: `{drift['current_model_key']}`")
    a(f"- frozen serving method drifted: **{drift['method_drifted']}**")
    for reason in drift["drift_reasons"]:
        a(f"  - {reason}")
    if drift["stale_model_keys"]:
        a(f"- stale model keys present in ledger: {sorted(drift['stale_model_keys'])}")
    a("- ledger: `localdata/ml_fade_research_ledger.json` (tracked; bot commits each run)")
    a("- state: `localdata/ml_fade_research_state.json` (tracked; checkpoint history)")
    a("- policy: `ML_FADE_RESEARCH_POLICY.md`")
    a("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# State transition on a completed checkpoint
# ---------------------------------------------------------------------------


def apply_checkpoint(
    state: dict,
    report: dict,
    *,
    now: str,
    report_path: str | None = None,
    studies: dict | None = None,
) -> dict:
    """Advance the checkpoint state (append-only history)."""
    state = dict(state)
    fade_settled = report["accrual"][FADE_FAMILY]["settled"]
    state["last_eval_at"] = now
    state["last_eval_settled_fade"] = fade_settled
    state["last_eval_active_day"] = report["today"]
    state["eval_count"] = int(state.get("eval_count") or 0) + 1
    state["model_drift"] = {
        "drifted": report["drift"]["method_drifted"],
        "reasons": report["drift"]["drift_reasons"],
        "model_key": report["drift"]["current_model_key"],
    }
    history = list(state.get("history") or [])
    history.append(
        {
            "eval_at": now,
            "due_reasons": list(report["due_reasons"]),
            "settled_fade": fade_settled,
            "rule_candidate": report["rule_candidate"]["status"],
            "warnings": list(report["warnings"]),
            "report_file": report_path,
            "studies": (studies or {}).get("outputs") or {},
        }
    )
    state["history"] = history
    return state
