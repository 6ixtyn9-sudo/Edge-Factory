#!/usr/bin/env python3
"""Dry-run or apply the audited restoration of the frozen Phase 5 incumbent."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.phase5_reconciliation import (  # noqa: E402
    EXPECTED_INCUMBENT_MODEL_KEY,
    Phase5ReconciliationError,
    apply_reconciliation,
    build_reconciliation_plan,
    verify_designated_baseline,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "localdata" / "edges_consensus.json")
    parser.add_argument("--activation-root", type=Path, default=ROOT / "localdata" / "phase5_activation")
    parser.add_argument("--audit-root", type=Path, default=ROOT / "localdata" / "phase5_reconciliation")
    parser.add_argument("--audit-id", default=None)
    parser.add_argument("--apply", action="store_true", help="write the audited reconciliation; default is read-only")
    args = parser.parse_args()

    try:
        if args.apply:
            result = apply_reconciliation(
                args.registry,
                args.activation_root,
                args.audit_root,
                audit_id=args.audit_id,
            )
            print(json.dumps({
                "status": "applied_and_read_back",
                "audit_dir": result["audit_dir"],
                "before_model_key": result["prepared"]["displaced_registry"]["ml_model_key"],
                "after_model_key": result["applied"]["registry_model_key"],
                "protected_cut_differences": result["prepared"]["displaced_registry"]["protected_cut_differences"],
                "preserved_statuses": result["prepared"]["planned_registry"]["preserved_statuses"],
                "guard": result["applied"]["guard"],
            }, indent=2, sort_keys=True))
            return 0

        baseline, _config, checks = verify_designated_baseline(args.activation_root)
        current = json.loads(args.registry.read_text(encoding="utf-8"))
        _planned, report = build_reconciliation_plan(current, baseline)
        print(json.dumps({
            "status": "dry_run_no_files_written",
            "designated_model_key": EXPECTED_INCUMBENT_MODEL_KEY,
            "baseline_verification": checks,
            "before_model_key": report["before_model_key"],
            "after_model_key": report["after_model_key"],
            "model_differences": report["model_differences"],
            "protected_cut_differences": report["protected_cut_differences"],
            "removed_extra_ml_meta_rules": report["extra_ml_meta_rules_removed"],
            "added_missing_ml_meta_rules": report["missing_ml_meta_rules_added_benched_or_baseline_status"],
            "preserved_statuses": report["preserved_statuses"],
            "preserved_non_ml_edge_count": report["preserved_non_ml_edge_count"],
            "preserved_ml_fade_edge_count": report["preserved_ml_fade_edge_count"],
        }, indent=2, sort_keys=True))
        return 0
    except (Phase5ReconciliationError, OSError, json.JSONDecodeError) as exc:
        print(f"PHASE5_RECONCILIATION blocked: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
