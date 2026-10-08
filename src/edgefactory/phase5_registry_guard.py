"""Operational guard for the frozen Phase 5 incumbent registry.

The legacy miner may continue producing research predictions and refreshing
unrelated non-ML edges. Its fitted ``ml_model`` and ML rule families are never
allowed to replace the live incumbent. A mismatch is reported and preserved;
this module never repairs the live registry by copying the baseline over it.
Pick scoring is fail-closed for ML when the live model/cuts do not match the
immutable Phase 5 baseline.
"""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from edgefactory.ml_fade_research import model_key
from edgefactory.phase5_activation import (
    Phase5ActivationError,
    _read_registry,
    _resolve_from_config,
    load_incumbent_state,
)

ML_RULE_PREFIXES = ("ml-meta", "ml-fade")
# Only decay/bench monitoring is permitted to vary an incumbent ML edge after
# its baseline is frozen. Miner statistics, definitions and other metadata are
# immutable for the purpose of operational scoring.
_DYNAMIC_EDGE_FIELDS = frozenset({"decay", "status", "benched_at"})


def is_ml_rule(rule: object) -> bool:
    return str(rule or "").strip().lower().startswith(ML_RULE_PREFIXES)


def _edge_map(
    edges: object,
    *,
    prefixes: tuple[str, ...] = ML_RULE_PREFIXES,
) -> tuple[dict[str, dict[str, Any]], str | None]:
    if not isinstance(edges, list):
        return {}, "registry edges is not a list"
    found: dict[str, dict[str, Any]] = {}
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        rule = edge.get("rule")
        if not str(rule or "").strip().lower().startswith(prefixes):
            continue
        if not isinstance(rule, str) or not rule.strip():
            return {}, "ML edge has no rule name"
        if rule in found:
            return {}, f"duplicate ML rule {rule}"
        found[rule] = edge
    return found, None


def _static_edge(edge: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in edge.items() if key not in _DYNAMIC_EDGE_FIELDS}


def _status_is_safe(baseline_status: object, live_status: object) -> bool:
    # Operational status may only move toward less eligibility. A certified
    # incumbent can be restricted to candidate/benched; a candidate can be
    # benched; and a baseline bench is immutable. No restricted status can be
    # promoted by the legacy miner or a stale registry write.
    if baseline_status == "certified":
        return live_status in {"certified", "candidate", "benched"}
    if baseline_status == "candidate":
        return live_status in {"candidate", "benched"}
    return live_status == baseline_status


def inspect_operational_registry(
    registry: dict[str, Any],
    activation_root: Path | str,
) -> dict[str, Any]:
    """Check a live registry against the immutable Phase 5 incumbent.

    Returns a secret-free report. Dynamic decay/bench fields are allowed only
    under the one-way status rule above; model bytes, cut identity, training /
    validation evidence, and the complete frozen ML-meta cut set must match.
    """
    report: dict[str, Any] = {
        "ok": False,
        "model_key": model_key(registry.get("ml_model")),
        "reason": None,
    }
    # NOTE: the module docstring's "never replace the live incumbent" invariant
    # is about the MINER. An era activated through the Phase 5 gate is a
    # deliberate, audited replacement, and this function verifies the live
    # registry against whichever era is active — incumbent while dormant or
    # killed, the activated candidate otherwise.
    try:
        baseline, config = load_incumbent_state(activation_root)
    except (Phase5ActivationError, OSError, ValueError, TypeError) as exc:
        report["reason"] = f"immutable Phase 5 state unavailable: {exc}"
        return report

    # The expectation follows the EFFECTIVE era, not the configured one: the
    # kill switch reverts the resolver to the incumbent while the config still
    # names the candidate, and revert_to_incumbent does the same deliberately.
    try:
        effective = _resolve_from_config(config, baseline, _read_registry(activation_root))
    except (Phase5ActivationError, OSError, ValueError, TypeError) as exc:
        report["reason"] = f"effective era could not be resolved: {exc}"
        return report
    if effective.get("effective_model_key") == baseline.get("incumbent_model_key"):
        expected_key = baseline.get("incumbent_model_key")
        expected_cuts_sha = baseline.get("incumbent_cuts_sha256")
        expected_cuts = baseline.get("incumbent_cuts")
        expected_label = "frozen incumbent"
    elif config.get("mode") == "candidate" and config.get("kill_switch") is False:
        # An ACTIVATED era becomes the expected live state; the frozen
        # incumbent baseline remains immutable history. Promotion is the only
        # writer that can put a candidate here, and it runs this same check on
        # the payload before writing — so the registry and the active config
        # cannot silently disagree about which model is live.
        expected_key = config.get("active_model_key")
        expected_cuts_sha = config.get("active_cuts_sha256")
        expected_cuts = config.get("candidate_cuts")
        expected_label = f"activated era {config.get('era_id') or '?'}"
    else:
        report["reason"] = (
            "effective Phase 5 era is neither the incumbent nor an activated "
            f"candidate (mode={config.get('mode')!r})"
        )
        return report
    if (
        not isinstance(registry.get("ml_model"), dict)
        or report["model_key"] != expected_key
    ):
        report["reason"] = (
            f"live model_key {report['model_key'] or 'missing'} does not match "
            f"{expected_label} {expected_key or 'missing'}"
        )
        return report
    if expected_label != "frozen incumbent" and (
        config.get("active_cuts_sha256") != expected_cuts_sha
    ):
        # The configured cut digest must describe the cut set the live
        # registry is being held to. (While dormant or killed the config may
        # still name a candidate's digest — the effective era is the baseline,
        # and the cut-set comparison below is what holds the line.)
        report["reason"] = "configured active cuts digest does not match the candidate cuts"
        return report

    expected_edges, expected_error = _edge_map(expected_cuts, prefixes=("ml-meta",))
    live_edges, live_error = _edge_map(
        registry.get("edges"), prefixes=("ml-meta",)
    )
    if expected_error or live_error:
        report["reason"] = expected_error or live_error
        return report
    if set(expected_edges) != set(live_edges):
        missing = sorted(set(expected_edges) - set(live_edges))
        added = sorted(set(live_edges) - set(expected_edges))
        report["reason"] = f"frozen ML cut set changed (missing={missing}, added={added})"
        return report

    for rule, expected in expected_edges.items():
        live = live_edges[rule]
        if _static_edge(live) != _static_edge(expected):
            report["reason"] = f"frozen ML cut payload changed: {rule}"
            return report
        if not _status_is_safe(expected.get("status"), live.get("status")):
            report["reason"] = (
                f"ML cut status was promoted or invalid: {rule} "
                f"({expected.get('status')} -> {live.get('status')})"
            )
            return report

    report.update({"ok": True, "reason": f"{expected_label} model/cuts verified"})
    return report


def preserve_live_ml_payload(
    candidate_registry: dict[str, Any],
    current_registry: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Merge a legacy miner result without replacing the live ML scorer.

    Candidate ML output is excluded from the operational registry. All current
    ``ml-meta`` and ``ml-fade`` entries (including decay fields and benches) and
    the current model payload are carried forward byte-for-value. New or
    changed non-ML entries from the miner are accepted unchanged.
    """
    safe = copy.deepcopy(candidate_registry)
    candidate_edges = candidate_registry.get("edges")
    if not isinstance(candidate_edges, list):
        candidate_edges = []

    current_edges = current_registry.get("edges") if isinstance(current_registry, dict) else []
    if not isinstance(current_edges, list):
        current_edges = []
    live_ml_edges = [copy.deepcopy(edge) for edge in current_edges
                     if isinstance(edge, dict) and is_ml_rule(edge.get("rule"))]
    allowed_non_ml_edges = [copy.deepcopy(edge) for edge in candidate_edges
                            if isinstance(edge, dict) and not is_ml_rule(edge.get("rule"))]
    safe["edges"] = allowed_non_ml_edges + live_ml_edges

    live_model = current_registry.get("ml_model") if isinstance(current_registry, dict) else None
    if isinstance(live_model, dict):
        safe["ml_model"] = copy.deepcopy(live_model)
    else:
        # Never adopt a newly fitted payload or silently restore from the
        # baseline when no live model is present. The scorer guard will block.
        safe.pop("ml_model", None)

    report = {
        "candidate_model_key": model_key(candidate_registry.get("ml_model")),
        "preserved_model_key": model_key(live_model),
        "preserved_ml_edge_count": len(live_ml_edges),
        "accepted_non_ml_edge_count": len(allowed_non_ml_edges),
        "baseline": None,
    }
    return safe, report
