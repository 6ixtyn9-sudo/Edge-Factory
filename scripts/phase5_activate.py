#!/usr/bin/env python3
"""Manage the dormant Phase 5 active-era config; activation is fail-closed."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.phase5_activation import (  # noqa: E402
    Phase5ActivationError,
    Phase5NotYetDue,
    activate_candidate,
    activation_status,
    dry_run_revert,
    initialize_activation_state,
    revert_to_incumbent,
    set_kill_switch,
)
from edgefactory.phase5_promotion import (  # noqa: E402
    Phase5PromotionError,
    promote_activated_candidate,
    restore_incumbent,
)


def _common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--root", type=Path, default=ROOT / "localdata" / "phase5_activation")


def _json_line(value: dict) -> None:
    print(json.dumps(value, sort_keys=True, separators=(",", ":")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)

    init_parser = commands.add_parser("initialize", help="freeze the incumbent model and ml-meta cuts")
    _common(init_parser)
    init_parser.add_argument(
        "--incumbent-registry", type=Path,
        default=ROOT / "localdata" / "edges_consensus.json",
    )

    status_parser = commands.add_parser("status", help="show configured and effective model state")
    _common(status_parser)

    dry_parser = commands.add_parser(
        "dry-run-revert", help="simulate kill/revert to immutable incumbent before activation"
    )
    _common(dry_parser)
    dry_parser.add_argument(
        "--certificate", type=Path,
        default=ROOT / "localdata" / "phase5_shadow" / "certification.json",
    )
    dry_parser.add_argument("--era-id", required=True)

    activate_parser = commands.add_parser("activate", help="activate only from a full passing verdict")
    _common(activate_parser)
    activate_parser.add_argument(
        "--certificate", type=Path,
        default=ROOT / "localdata" / "phase5_shadow" / "certification.json",
    )
    activate_parser.add_argument(
        "--incumbent-registry", type=Path,
        default=ROOT / "localdata" / "edges_consensus.json",
    )
    activate_parser.add_argument("--era-id", required=True)
    activate_parser.add_argument("--confirm", action="store_true")

    promote_parser = commands.add_parser(
        "promote", help="write the activated era into the served registry (dry run without --confirm)"
    )
    _common(promote_parser)
    promote_parser.add_argument(
        "--registry", type=Path,
        default=ROOT / "localdata" / "edges_consensus.json",
    )
    promote_parser.add_argument("--era-id", required=True)
    promote_parser.add_argument("--confirm", action="store_true")

    restore_parser = commands.add_parser(
        "restore", help="write the frozen incumbent back into the served registry"
    )
    _common(restore_parser)
    restore_parser.add_argument(
        "--registry", type=Path,
        default=ROOT / "localdata" / "edges_consensus.json",
    )
    restore_parser.add_argument("--confirm", action="store_true")

    kill_parser = commands.add_parser("kill-switch", help="immediately force resolver to incumbent")
    _common(kill_parser)

    revert_parser = commands.add_parser("revert", help="one-command return to immutable incumbent")
    _common(revert_parser)

    args = parser.parse_args()
    try:
        if args.command == "initialize":
            result = initialize_activation_state(args.root, args.incumbent_registry)
        elif args.command == "status":
            result = activation_status(args.root)
        elif args.command == "dry-run-revert":
            result = dry_run_revert(
                args.root, args.certificate, era_id=args.era_id
            )
        elif args.command == "activate":
            result = activate_candidate(
                args.root, args.certificate, args.incumbent_registry,
                era_id=args.era_id, confirmed=args.confirm,
            )
        elif args.command == "promote":
            result = promote_activated_candidate(
                args.root, args.registry, era_id=args.era_id, write=args.confirm,
            )
        elif args.command == "restore":
            result = restore_incumbent(
                args.root, args.registry, write=args.confirm,
            )
        elif args.command == "kill-switch":
            result = set_kill_switch(args.root)
        else:
            result = revert_to_incumbent(args.root)
    except Phase5NotYetDue as exc:
        _json_line({"status": "not_yet_due", "reason": str(exc)})
        return 0 if args.command == "dry-run-revert" else 2
    except (Phase5ActivationError, Phase5PromotionError) as exc:
        _json_line({"status": "blocked", "reason": str(exc)})
        return 2
    _json_line(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
