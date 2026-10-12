#!/usr/bin/env python3
"""§4.5 — the politeness/receipt lines, printed raw from the shipped code.

What this proves and what it cannot:

* the interval between market requests and the run budgets are read off the
  adapter's own source (file + symbol, never a copied constant);
* a capture is driven with the TRANSPORT stubbed (no vendor request from this
  workspace), and the receipt it returns is printed whole, so the
  `requests` / `market_requests` / `market_budget_stop` keys are shown as the
  wrapper actually emits them;
* the politeness module's tests are collected and run by name.

The live receipt lines (real requests against BetExplorer) come from the
operator's own service run, not from here: bash has no route to the site, and
the shipped code's network surface is the one the operator dispatches.
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.sources import betexplorer_odds as be  # noqa: E402

print("== 1. the interval and the budgets, read off the adapter's source ==")
src = (ROOT / "src/edgefactory/sources/betexplorer_odds.py").read_text()
for sym in ("_MARKET_INTERVAL", "_MAX_MARKET_ROWS", "_MAX_MARKET_LINES",
            "_MAX_H2H_ROWS", "_MAX_STANDINGS_ROWS", "_MAX_FETCHES_PER_RUN"):
    m = re.search(rf"^{sym}\s*(?::[^=]+)?=\s*(.+)$", src, re.M)
    print(f"  {sym:22s} = {m.group(1).strip() if m else 'NOT FOUND'}")
print("  (every market request is made through the same interval-gated fetch:")
print(f"   {[l.strip() for l in src.splitlines() if 'min_interval=_MARKET_INTERVAL' in l]})")

print()
print("== 2. the budget-stop line and the counters the receipt whitelists ==")
print(f"  request_stats()  = {json.dumps(be.request_stats(), sort_keys=True)}")
sys.path.insert(0, str(ROOT))                     # scripts/ is a repo-root package
import scripts.capture_betexplorer as capture  # noqa: E402

print(f"  RECEIPT_STAT_KEYS = {sorted(capture.RECEIPT_STAT_KEYS)}")
print("  the stop flag is raised by the tab loop; the constant it prints is")
print("  the key name above (`market_budget_stop`), asserted by")
print("  tests/test_betexplorer_politeness.py and printed here from the module.")

print()
print("== 3. a capture with the transport stubbed: the receipt, whole ==")
import tempfile  # noqa: E402

from tests.test_betexplorer_match_detail import PICK, _reset_be, _run_pick  # noqa: E402

tmp = pathlib.Path(tempfile.mkdtemp(prefix="s45_receipt_"))
# BOTH modules write under their own module-level LOCALDATA at call time (the
# odds cache and the per-match detail ledger in the adapter, the receipt in the
# wrapper). Point both at a scratch directory before anything runs: a demo run
# must never write the repository's real state.
_orig_localdata = (capture.LOCALDATA, be.LOCALDATA)
capture.LOCALDATA = be.LOCALDATA = tmp
calls: list[str] = []
_run_pick(PICK, calls=calls)
try:
    receipt = capture.capture("2026-10-12", max_fixtures=1)
except TypeError:                                  # pragma: no cover - signature drift
    receipt = capture.capture("2026-10-12")
shown = {k: receipt.get(k) for k in sorted(receipt)
         if k in capture.RECEIPT_STAT_KEYS or k in {"fixtures", "markets"}}
print(json.dumps(shown, indent=2, sort_keys=True, default=str))

print()
print("== 4. the politeness module, collected and run by name ==")
for module in ("tests/test_betexplorer_politeness.py",
               "tests/test_betexplorer_match_detail.py"):
    out = subprocess.run([sys.executable, "-m", "pytest", module, "-q",
                          "-p", "no:randomly", "--collect-only"],
                         cwd=ROOT, capture_output=True, text=True,
                         env={**__import__("os").environ,
                              "PYTHONPATH": str(ROOT / "src")}).stdout
    names = [l for l in out.splitlines() if "::" in l]
    print(f"  {module}: {len(names)} test(s)")
    tail = [l for l in out.splitlines() if "test" in l and "::" not in l][-1:]
    print(f"    ({tail[0].strip() if tail else '?'})")
capture.LOCALDATA, be.LOCALDATA = _orig_localdata   # restored; the scratch copy stays behind
print()
print("== 5. the repository's own state files, checked after the run ==")
git_status = subprocess.run(["git", "status", "--porcelain", "--", "localdata/"],
                            cwd=ROOT, capture_output=True, text=True).stdout.strip()
print(f"  git status --porcelain -- localdata/  ->  "
      f"{git_status if git_status else '(empty: the demo wrote no real state)'}")

run = subprocess.run([sys.executable, "-m", "pytest",
                      "tests/test_betexplorer_politeness.py", "tests/test_betexplorer_match_detail.py",
                      "-q", "-p", "no:randomly"], cwd=ROOT, capture_output=True, text=True,
                     env={**__import__("os").environ, "PYTHONPATH": str(ROOT / "src")}).stdout
print("  " + run.strip().splitlines()[-1])
