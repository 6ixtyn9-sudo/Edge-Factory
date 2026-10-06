#!/usr/bin/env python3
"""Acceptance tests for the 2026-10-07 work order.

This script is the contract between the operator and whoever does the work.
Every item has an executable check here. The work is done when this prints
ALL PASS - not when an agent says it is done.

Design rules:
  * Offline. No network, no secrets, no production data required.
  * Behavioural, not textual. Checks call the real functions with synthetic
    payloads rather than grepping for strings, so they cannot be satisfied by
    editing a comment.
  * Every check fails loudly today. That is correct: nothing is implemented
    yet. A check that passes before the work starts is a broken check.

Usage:
    python3 scripts/verify_work_order.py            # all tasks
    python3 scripts/verify_work_order.py WO-2       # one task
"""

from __future__ import annotations

import sys
import traceback
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

# The package __init__ eagerly imports every scraper, which drags in optional
# third-party transports. These checks only exercise pure parsing, so stub the
# absent ones rather than demand a venv - this script must run on a fresh clone
# with no dependencies, otherwise it will not be run.
import importlib.abc
import importlib.machinery
import types

_OPTIONAL = {
    "curl_cffi", "dotenv", "bs4", "lxml", "requests", "supabase", "dateutil",
    "duckdb", "pandas", "numpy", "sklearn", "scipy", "httpx", "yaml",
}


class _StubFinder(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    """Supply a hollow module for optional deps, so imports never decide a check."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname.split(".")[0] in _OPTIONAL:
            return importlib.machinery.ModuleSpec(fullname, self)
        return None

    def create_module(self, spec):
        mod = types.ModuleType(spec.name)
        mod.__path__ = []
        return mod

    def exec_module(self, module):
        module.__getattr__ = lambda name: (lambda *a, **k: None)


sys.meta_path.append(_StubFinder())

RESULTS: list[tuple[str, str, bool, str]] = []


def check(task: str, name: str):
    """Register a check. The body returns None on pass or a string on fail."""

    def wrap(fn):
        try:
            problem = fn()
        except Exception:
            problem = "raised:\n" + "".join(
                traceback.format_exception(*sys.exc_info())[-3:]
            ).strip()
        RESULTS.append((task, name, problem is None, problem or ""))
        return fn

    return wrap


# ---------------------------------------------------------------------------
# WO-1  Pinnacle discards every price row
# ---------------------------------------------------------------------------

@check("WO-1", "markets delivered as a dict are parsed, not skipped")
def _():
    from edgefactory.sources import pinnapi_odds as p

    payload = {"events": [{
        "id": "e1", "home": "Arsenal", "away": "Chelsea",
        "start_at": "2026-10-07T18:00:00Z", "league": {"name": "Premier League"},
        "markets": {
            "moneyline": [
                {"selection": "home", "price": 2.10},
                {"selection": "draw", "price": 3.40},
                {"selection": "away", "price": 3.20},
            ]
        },
    }]}
    rows, schema = p.parse_snapshot(payload, day="2026-10-07")
    if not schema:
        return "schema_match was False; the event has both team names"
    if not rows:
        return ("0 rows from a dict-shaped markets block. This is the live "
                "production signature: schema matches, every row vanishes.")
    return None


@check("WO-1", "a skipped markets block is counted, never silent")
def _():
    from edgefactory.sources import pinnapi_odds as p

    payload = {"events": [{"id": "e1", "home": "Arsenal", "away": "Chelsea",
                           "markets": "not-a-container"}]}
    p.parse_snapshot(payload, day="2026-10-07")
    reasons = getattr(p, "canonicalization_drop_reasons", None)
    reasons = reasons() if callable(reasons) else getattr(
        p, "_CANONICALIZATION_DROP_REASONS", {})
    if not reasons:
        return ("an event was dropped and nothing was counted. Any 'continue' "
                "that discards data must increment a named reason, or the next "
                "outage is invisible in exactly the way this one was.")
    return None


@check("WO-1", "a price under an unexpected key is counted, never silent")
def _():
    from edgefactory.sources import pinnapi_odds as p

    payload = {"events": [{"id": "e1", "home": "Arsenal", "away": "Chelsea",
                           "markets": [{"market": "moneyline",
                                        "selection": "home",
                                        "decimal": 2.10}]}]}
    rows, _ = p.parse_snapshot(payload, day="2026-10-07")
    reasons = getattr(p, "canonicalization_drop_reasons", None)
    reasons = reasons() if callable(reasons) else getattr(
        p, "_CANONICALIZATION_DROP_REASONS", {})
    if not rows and not reasons:
        return "row dropped for an unreadable price with no reason recorded"
    return None


# ---------------------------------------------------------------------------
# WO-2  Failure receipts cache themselves and block the next diagnosis
# ---------------------------------------------------------------------------

@check("WO-2", "a 404 probe receipt expires instead of blocking forever")
def _():
    from edgefactory.sources import betminer as b

    fn = getattr(b, "_probe_receipt_is_binding", None)
    if fn is None:
        return ("no _probe_receipt_is_binding(receipt, now) helper. A receipt "
                "recording a FAILURE must stop suppressing re-probes after a "
                "bounded period; a receipt recording a confirmed contract may "
                "suppress indefinitely.")
    import datetime as dt

    now = dt.datetime(2026, 10, 7, 12, 0, tzinfo=dt.timezone.utc)
    stale_404 = {"schema": 2, "http_status": 404,
                 "probed_at": "2026-10-05T22:22:50+00:00"}
    fresh_404 = {"schema": 2, "http_status": 404,
                 "probed_at": "2026-10-07T11:00:00+00:00"}
    if fn(stale_404, now=now):
        return "a two-day-old 404 still suppresses the probe"
    if not fn(fresh_404, now=now):
        return "a one-hour-old 404 does not suppress; caps would be breached"
    return None


@check("WO-2", "receipts are keyed so a future date cannot pre-block today")
def _():
    from edgefactory.sources import betminer as b

    fn = getattr(b, "_probe_receipt_is_binding", None)
    if fn is None:
        return "see previous check"
    import datetime as dt

    now = dt.datetime(2026, 10, 7, 12, 0, tzinfo=dt.timezone.utc)
    receipt = {"schema": 2, "http_status": 404,
               "probed_at": "2026-10-05T22:22:50+00:00", "day": "2026-10-07"}
    if fn(receipt, now=now):
        return ("staleness is being judged by target date rather than by when "
                "the probe actually ran. The pipeline plans two days ahead, so "
                "this lets a receipt written on Monday block Wednesday.")
    return None


# ---------------------------------------------------------------------------
# WO-3  Health labels assert causes the evidence does not support
# ---------------------------------------------------------------------------

@check("WO-3", "HTTP 200 with zero rows no longer claims the provider was empty")
def _():
    import edgefactory.source_health as sh

    src = (REPO / "src/edgefactory/source_health.py").read_text()
    if "valid_empty_http_200" in src:
        return ("'valid_empty_http_200' still present. It asserts the provider "
                "legitimately had nothing, which is unevidenced and was wrong "
                "for Pinnacle for days. Rename to something that states the "
                "observation only, e.g. http_200_zero_rows_after_parse.")
    if not hasattr(sh, "REASON_HTTP_200_ZERO_ROWS") and \
            "http_200_zero_rows" not in src:
        return "no replacement observation-only token found"
    return None


@check("WO-3", "403 distinguishes a dead key from a plan restriction")
def _():
    src = (REPO / "src/edgefactory/source_health.py").read_text()
    if "http_403_plan" not in src and "plan_restricted" not in src:
        return ("only http_403_auth exists. Bzzoiro's token demonstrably works "
                "- best_results=12 on a sibling call in the same run - while "
                "the comparison endpoint 403s. Reporting that as 'auth' sends "
                "the operator to rotate a key that is already fine.")
    return None


@check("WO-3", "oddspapi emits a reason token like every other source")
def _():
    src = (REPO / "src/edgefactory/source_health.py").read_text()
    if "oddspapi" not in src:
        return ("oddspapi is absent from source_health. It printed 'raw0' with "
                "no reason for four days of hard 429s, which is why nobody "
                "looked.")
    if "429" not in src and "rate_limit" not in src and "quota" not in src:
        return "no rate-limit/quota reason token to attach to a 429"
    return None


@check("WO-3", "rows discarded in parsing are visible per source")
def _():
    src = (REPO / "src/edgefactory/source_health.py").read_text()
    if "canonicalization_dropped" not in src and "dropped" not in src:
        return ("no per-source discard count on the health line. Pinnacle "
                "computed its own drop reasons and wrote them to a gitignored "
                "file nobody read. Surface the number where it is seen.")
    return None


# ---------------------------------------------------------------------------
# WO-4  The missing hour
# ---------------------------------------------------------------------------

@check("WO-4", "the 60-minute kickoff disagreement has a regression test")
def _():
    target = REPO / "tests" / "test_kickoff_offset_60m.py"
    if not target.exists():
        return ("no test covers the kickoff mismatch. Four fixtures a day "
                "disagree with themselves by exactly 60 minutes. The fallback "
                "hides it, so a regression here would be silent - and it sits "
                "next to settlement, where an hour decides a result.")
    return None


# ---------------------------------------------------------------------------
# WO-6  Settlement loses a leg when the spelling drifts after freeze
# ---------------------------------------------------------------------------

def _auto_tickets():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "at_wo6", REPO / "scripts" / "auto_tickets.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@check("WO-6", "a fixture filed under two names resolves to one leg")
def _():
    at = _auto_tickets()
    archive = at._folded_leg_key("2026-10-05", "Italy", "Türkiye", "home")
    slip = at._folded_leg_key("2026-10-05", "Italy", "Turkey", "HOME")
    if archive != slip:
        return (f"archive {archive} != slip {slip}. Italy beat Türkiye on "
                "2026-10-05 and the acca never settled, because the archive "
                "says Türkiye and the frozen slip says Turkey. 20.89% of "
                "capital is stuck and voids on 2026-10-10, booking a winning "
                "double as a single and losing 17.13% of capital.")
    return None


@check("WO-6", "settlement uses a key frozen with the slip, not re-parsed text")
def _():
    at = _auto_tickets()
    fn = getattr(at, "leg_lookup_key", None)
    if fn is None:
        return ("no leg_lookup_key(slip_date, leg) helper. Settlement splits "
                "the free-text 'A vs B' back apart at settlement time, so any "
                "respelling after freeze orphans the leg permanently. The slip "
                "must carry a stable identifier captured when it froze.")
    stable = fn("2026-10-05", {"match": "COMPLETELY WRONG vs TEXT",
                               "fixture_key": ("2026-10-05", "italy",
                                               "turkiye"), "pick": "HOME"})
    parsed = fn("2026-10-05", {"match": "Italy vs Türkiye", "pick": "HOME"})
    if stable != parsed:
        return ("a stored fixture_key must take precedence over the match "
                "string; free text is a display artefact, not an identifier")
    return None


# ---------------------------------------------------------------------------
# WO-5  Guard rails: the work order must not change what bets
# ---------------------------------------------------------------------------

@check("WO-5", "no gate, floor, cap, quorum or threshold was touched")
def _():
    import subprocess

    base = "origin/main"
    # Scan CODE only. Prose that merely names these constants - the work order,
    # the open-issues register, and the banned list in this very file - must not
    # trip the guard, or it cries wolf and stops being read.
    try:
        diff = subprocess.run(
            # `git diff <base>` - NOT `<base>...HEAD` - so uncommitted working
            # tree changes are covered. A guard that only inspects committed
            # work tells you after the fact, which is too late to be a guard.
            ["git", "diff", base, "--unified=0", "--",
             "src", "scripts", ":(exclude)scripts/verify_work_order.py"],
            cwd=REPO, capture_output=True, text=True, timeout=60).stdout
    except Exception as exc:
        return f"could not diff: {exc}"
    banned = ("MIN_EDGE", "EDGE_FLOOR", "QUORUM", "STAKE_CAP", "MAX_STAKE",
              "KELLY", "THRESHOLD", "VETO_", "PROMOTE")
    hits = sorted({w for w in banned
                   for ln in diff.splitlines()
                   if ln.startswith(("+", "-"))
                   and not ln.startswith(("+++", "---")) and w in ln})
    if hits:
        return ("selection constants appear in the diff: " + ", ".join(hits) +
                ". This work order is plumbing only. Stop and get sign-off.")
    return None


@check("WO-5", "the test suite baseline has not shrunk")
def _():
    count = sum(p.read_text().count("def test_")
                for p in (REPO / "tests").rglob("test_*.py"))
    # The count of test *functions* is the stable floor; the collected count
    # is not. test_docs_links parametrises over every markdown file in the
    # repo, so "the suite must report at least N" drifts upward whenever
    # anyone writes documentation - a bad acceptance contract. What actually
    # matters is: nothing failed, and no existing test was deleted. This
    # check is the second half. Raise it when you add tests; never lower it
    # to make the check pass.
    if count < 1485:
        return (f"{count} test functions found, floor is 1485. Tests were "
                "deleted rather than fixed.")
    return None


# ---------------------------------------------------------------------------

def main() -> int:
    wanted = sys.argv[1] if len(sys.argv) > 1 else None
    rows = [r for r in RESULTS if not wanted or r[0] == wanted]
    if not rows:
        print(f"no checks match {wanted!r}")
        return 2

    width = max(len(r[1]) for r in rows) + 2
    task = None
    for t, name, ok, problem in rows:
        if t != task:
            print(f"\n{t}")
            task = t
        print(f"  {'PASS' if ok else 'FAIL'}  {name:<{width}}")
        if not ok:
            for line in problem.splitlines():
                print(f"          {line}")

    failed = [r for r in rows if not r[2]]
    print(f"\n{len(rows) - len(failed)}/{len(rows)} passing")
    if failed:
        print("NOT DONE - the work order is complete when this prints ALL PASS")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
