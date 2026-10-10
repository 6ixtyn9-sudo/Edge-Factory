#!/usr/bin/env python3
"""Find deployment settings that silently override a code default.

Why this exists
---------------
The SharpAPI price source was repaired on 2026-10-03 by correcting its
default endpoint. The repair never reached production: the workflow pinned
``SHARPAPI_ENDPOINT`` to a different value, which overrode the corrected
default for three days while every diagnostic reported a vendor problem.
Nothing in the code, the tests or the logs could see it, because each half
was internally consistent and only the PAIR was wrong.

That is a class, not an incident. This script enumerates every environment
variable the workflows set, resolves what the code would have used instead,
and reports every disagreement.

Scope and limits, stated because a number without its scope is a trap
---------------------------------------------------------------------
Covered: literal and module-constant defaults in ``src/**.py`` and
``scripts/**.py``, compared against ``.github/workflows/*.y*ml``.

NOT covered: defaults computed at runtime (a call, a conditional, a dict
lookup). Those cannot be resolved statically. As of this writing there are
some such reads and NONE of them should be set by any workflow, so the blind
spot must not hide anything -- but that is a fact about today, and the check
``--strict`` performs (and ``test_the_blind_spot_does_not_hide_a_deployed_variable``)
re-verifies it on every run rather than trusting this sentence. A read whose
name comes from a module constant resolves too, so a credential ring written as
``os.environ.get(KEY_ENV)`` is no longer counted as unresolvable.

Consumers outside ``src``/``scripts`` are also invisible: the Forebet
diagnostic workflow reads its variables in an inline heredoc, so those look
like orphans and are listed separately rather than reported as faults.
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
NAME_RE = re.compile(r"[A-Z_][A-Z0-9_]*$")

# Divergences that are intentional. Each needs a reason, because an
# allowlist without reasons becomes a place to hide the next defect.
ACCEPTED = {
    # The adapter refuses to run without an explicit sport filter; the empty
    # code default IS the fail-closed behaviour. Production supplies the
    # value. Agreement here would defeat the guard.
    "SHARPAPI_SPORT": "code default is empty on purpose: fail closed until configured",
    # Off by default in code, switched on for the scheduled run.
    "EDGE_FACTORY_ODDSPAPI_PRICES": "feature flag: off in code, enabled by the deployment",
    # Deliberate credit rationing: each market costs one credit per event,
    # so the six-market code default would triple spend against a 480/month
    # cap. Documented in TICKETS-OPEN (n) because the companion knob
    # ODDS_API_TOTAL_POINTS was NOT narrowed to match.
    "ODDS_API_MARKETS": "deliberate credit rationing; see TICKETS-OPEN (n)",
}

# Divergences that are NOT accepted - they are known defects awaiting a
# manual step. Kept separate from ACCEPTED on purpose: an approval and an
# outstanding debt must not look alike in a config file, or the debt stops
# being paid. Delete the entry when the step is done; the audit will then
# confirm the two sides agree.
PENDING_WORKFLOW_APPLY: dict[str, str] = {
    # Empty, and that is the point. The SharpAPI endpoint entry lived here
    # until the corrected workflow was applied on 2026-10-06 (main commit
    # eed2bfe6, byte-identical to the file proposed here). The stale-entry
    # test then failed and demanded this removal, which is the mechanism
    # working: a paid debt must disappear from the record rather than
    # linger where it would pre-approve the next divergence.
}


def workflow_env() -> dict[str, tuple[str | None, str]]:
    """Every env assignment in every workflow, with its '||' fallback."""
    found: dict[str, tuple[str | None, str]] = {}
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            match = re.match(r"\s+([A-Z_][A-Z0-9_]*):\s*(.+?)\s*$", line)
            if not match:
                continue
            name, raw = match.groups()
            where = f"{path.name}:{lineno}"
            fallback = re.search(r"\|\|\s*'([^']*)'\s*}}", raw)
            if fallback:
                found[name] = (fallback.group(1), where)
            elif "${{" in raw:
                found[name] = (None, where)        # secret with no fallback
            else:
                found[name] = (raw.strip("'\""), where)
    return found


def _module_constants(tree: ast.Module) -> dict[str, object]:
    consts: dict[str, object] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    consts[target.id] = node.value.value
    return consts


def _env_name(arg: ast.AST, consts: dict[str, object]) -> str | None:
    """The variable name an ``os.environ.get(...)`` argument refers to.

    ``os.environ.get("X")`` and ``os.environ.get(KEY_ENV)`` are the same read -
    a module constant holding the name is exactly how the SharpAPI defect hid
    once - so both must resolve. Resolution only ever ADDS coverage: a name we
    cannot resolve is still left alone rather than guessed at.
    """
    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
        return arg.value
    if isinstance(arg, ast.Name) and isinstance(consts.get(arg.id), str):
        return consts[arg.id]
    return None


def _is_env_get(node: ast.AST, consts: dict[str, object] | None = None) -> bool:
    """An ``os.environ.get(NAME)`` read.

    With ``consts`` the first argument may also be a module constant holding the
    name. The parameter is OPTIONAL and only the fallback-chain check passes it:
    widening the first-name detection would newly expose reads such as
    ``os.environ.get(FOREGROUND_ENV, "auto")`` whose divergence nobody has
    reviewed yet, and this audit must fix its blind spot without quietly
    re-opening the case book.
    """
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("get", "getenv") and bool(node.args)):
        return False
    name = _env_name(node.args[0], consts or {})
    return bool(name) and bool(NAME_RE.match(name))


def code_defaults() -> tuple[dict[str, set[tuple[str, str]]], set[str]]:
    """Map env var -> {(default, location)}, plus the unresolvable set."""
    defaults: dict[str, set[tuple[str, str]]] = {}
    blind: set[str] = set()
    sources = sorted(ROOT.joinpath("src").rglob("*.py")) + sorted(ROOT.joinpath("scripts").rglob("*.py"))
    for path in sources:
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, UnicodeDecodeError):
            continue
        consts = _module_constants(tree)
        rel = path.relative_to(ROOT)

        def terminal(value: ast.AST) -> ast.AST:
            """Walk a 'A or B or ""' fallback chain to its final value.

            A credential ring reads like os.environ.get("X_KEYS") or
            os.environ.get("X_KEY") or "". The fallback for the first name is
            another env var, not a literal, so there is no code default for a
            deployment to contradict. Resolving to the end of the chain keeps
            these out of the blind-spot count, which would otherwise imply an
            unverifiable gap where none exists.
            """
            while isinstance(value, ast.BoolOp) and isinstance(value.op, ast.Or):
                value = value.values[-1]
            return value

        def record(name: str, value: ast.AST, lineno: int) -> None:
            value = terminal(value)
            if _is_env_get(value, consts):
                return   # fallback is another env var: nothing to contradict
            if isinstance(value, ast.Constant):
                defaults.setdefault(name, set()).add((str(value.value), f"{rel}:{lineno}"))
            elif isinstance(value, ast.Name) and value.id in consts:
                defaults.setdefault(name, set()).add((str(consts[value.id]), f"{rel}:{lineno}"))
            else:
                blind.add(name)

        for node in ast.walk(tree):
            # os.environ.get("X", default)
            if _is_env_get(node) and len(node.args) == 2:
                record(node.args[0].value, node.args[1], node.lineno)
            # os.environ.get("X") or fallback
            if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or) and len(node.values) >= 2:
                head = node.values[0]
                if _is_env_get(head) and len(head.args) == 1:
                    record(head.args[0].value, node.values[1], node.lineno)
    return defaults, blind


def drift() -> list[tuple[str, str, str, str, str]]:
    """Every workflow pin that contradicts a resolvable code default."""
    wf = workflow_env()
    code, _blind = code_defaults()
    out = []
    for name, (pinned, where) in sorted(wf.items()):
        if pinned is None or name not in code:
            continue
        for value, location in sorted(code[name]):
            if value != pinned:
                out.append((name, pinned, value, location, where))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true",
                        help="exit non-zero on any divergence outside the allowlist")
    args = parser.parse_args()

    rows = drift()
    _code, blind = code_defaults()
    wf = workflow_env()

    unexpected = [r for r in rows if r[0] not in ACCEPTED and r[0] not in PENDING_WORKFLOW_APPLY]
    print(f"{'ENV VAR':<32}{'DEPLOYMENT':<20}{'CODE DEFAULT':<24}STATUS")
    print("-" * 96)
    for name, pinned, value, location, where in rows:
        status = ("accepted" if name in ACCEPTED
                  else "PENDING MANUAL APPLY" if name in PENDING_WORKFLOW_APPLY
                  else "DRIFT")
        print(f"{name:<32}{pinned[:18]:<20}{value[:22]:<24}{status}")
        print(f"{'':<32}{where:<20}{location}")
    if not rows:
        print("(no divergences at all)")

    overlap = sorted(blind & set(wf))
    print()
    pending = [r for r in rows if r[0] in PENDING_WORKFLOW_APPLY]
    print(f"{len(rows)} divergence(s): {len(rows) - len(unexpected) - len(pending)} accepted, "
          f"{len(pending)} pending a manual step, {len(unexpected)} unreviewed.")
    for name, *_ in pending:
        print(f"  PENDING {name}: {PENDING_WORKFLOW_APPLY[name]}")
    print(f"Blind spot: {len(blind)} env var(s) have a default this script cannot resolve; "
          f"{len(overlap)} of those are workflow-set{' -> ' + ', '.join(overlap) if overlap else ' (so none are hidden)'}.")

    if args.strict and (unexpected or overlap):
        for name, pinned, value, location, where in unexpected:
            print(f"\nUNREVIEWED: {name} is {pinned!r} at {where} but {value!r} at {location}.")
            print("  Either fix one side, or add it to ACCEPTED with a reason.")
        for name in overlap:
            print(f"\nUNRESOLVABLE AND DEPLOYED: {name} has a computed default and is set by a "
                  "workflow; this script can no longer prove the two agree.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
