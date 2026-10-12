#!/usr/bin/env bash
# A3(b) of the 2026-10-12 close-out: the receipt-whitelist reconciliation.
#
# The reviewer reconstructed the patch's whitelist literal as SEVEN keys and
# asked how that squares with the round's N-3 phrasing "5+3 -> 8". This script
# prints both literals from the sources (the patch file itself, and the module
# at this tip), both producers' field sets, which keys a test pins, and the
# reconciliation.
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/a3b_whitelist_table.sh
set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

echo "=== A3(b): receipt-whitelist reconciliation, tip $(git rev-parse --short HEAD) ==="
echo
echo '$ sed -n "/if key in {/,+2p" handoff/betexplorer-depth.patch   # the patch literal (post-image)'
grep -n -A 2 "if key in {" handoff/betexplorer-depth.patch | sed -n '1,12p'
echo
echo '$ grep -n "RECEIPT_STAT_KEYS = frozenset" -A 5 scripts/capture_betexplorer.py'
grep -n "RECEIPT_STAT_KEYS = frozenset" -A 5 scripts/capture_betexplorer.py
echo
echo '$ grep -n "^def run_stats" -A 10 src/edgefactory/sources/betexplorer_odds.py   # at the tip'
grep -n "^def run_stats" -A 10 src/edgefactory/sources/betexplorer_odds.py | head -12
echo
echo '$ git show origin/main:src/edgefactory/sources/betexplorer_odds.py | grep -A 8 "^def run_stats"'
git show origin/main:src/edgefactory/sources/betexplorer_odds.py | grep -A 8 "^def run_stats" | head -10
echo
echo '$ grep -rn "be_fetches" src/ scripts/ tests/ --include=*.py'
grep -rn "be_fetches" src/ scripts/ tests/ --include=*.py || true
echo

PYTHONPATH=src .venv/bin/python - <<'PY'
"""Render the reconciliation table from the sources themselves."""
import re
import subprocess
from pathlib import Path

root = Path(".")
# the patch POST-image literal: the '+' line that opens it, plus its
# continuations up to the closing brace. (The '-' line above it is the
# pre-image, four keys - taking that one is exactly the confusion this table
# exists to settle.)
patch_lines = Path("handoff/betexplorer-depth.patch").read_text().splitlines()
start = next(i for i, ln in enumerate(patch_lines)
             if ln.startswith("+") and "if key in {" in ln and "requests" in
             "".join(patch_lines[i:i + 3]))
literal = []
for ln in patch_lines[start:]:
    literal.append(ln)
    if "}" in ln:
        break
# the diff marker and indentation are transport, not code:
# strip them before reading the literal, or the key tokens
# come out as '+    "requests"'
patch_literal = "\n".join(ln[1:] if ln.startswith("+") else ln
                              for ln in literal)
patch_keys = [k.strip().strip('"') for k in
              re.search(r"\{([^}]*)\}", patch_literal, re.S).group(1).split(",")]
patch_keys = [k for k in patch_keys if k]
assert "requests" in patch_keys, "took the pre-image literal, not the post-image"

capture = Path("scripts/capture_betexplorer.py").read_text()
tip_keys = [k.strip().strip('"') for k in
            re.search(r"RECEIPT_STAT_KEYS = frozenset\(\{([^}]*)\}\)", capture, re.S)
            .group(1).split(",")]
tip_keys = [k for k in tip_keys if k]

odds = Path("src/edgefactory/sources/betexplorer_odds.py").read_text()
run_keys = re.findall(r'"(be_[a-z0-9_]+)":', re.search(
    r"def run_stats\(\).*?return \{(.*?)\n    \}", odds, re.S).group(1))
req_keys = re.findall(r'"(requests|market_requests|market_budget_stop)"', re.search(
    r"def request_stats\(\).*?return \{(.*?)\}\n", odds, re.S).group(1))

origin_run = subprocess.run(
    ["git", "show", "origin/main:src/edgefactory/sources/betexplorer_odds.py"],
    capture_output=True, text=True).stdout
origin_keys = re.findall(r'"(be_[a-z0-9_]+)":', re.search(
    r"def run_stats\(\).*?return \{(.*?)\n    \}", origin_run, re.S).group(1))

pinned = {
    "be_429": "tests/test_betexplorer_politeness.py (429 floor + cooldown tests)",
    "be_cooling_down": "tests/test_betexplorer_politeness.py (429 floor + cooldown tests)",
    "be_cached": "tests/test_betexplorer_politeness.py "
                 "(test_same_day_fixture_cache_dedupes_requests_and_survives_run_reset)",
    "be_fetches": "tests/test_capture_betexplorer.py (run_stats stub only - see below)",
    "requests": "tests/test_betexplorer_politeness.py "
                "(test_request_counts_track_every_attempt_for_the_receipt)",
    "market_requests": "tests/test_betexplorer_match_detail.py "
                       "(test_market_tabs_stop_at_the_run_request_budget)",
    "market_budget_stop": "tests/test_betexplorer_match_detail.py "
                          "(test_market_tabs_stop_at_the_run_request_budget)",
    "be_rows_rejected": "tests/test_betexplorer_match_detail.py "
                        "(test_receipt_keeps_the_row_refusal_census)",
    "be_rows_rejected_reasons": "tests/test_betexplorer_match_detail.py "
                                "(test_receipt_keeps_the_row_refusal_census)",
}

all_keys = sorted(set(patch_keys) | set(tip_keys) | set(run_keys) | set(req_keys))
print(f"{'receipt key':26} {'patch lit.':10} {'tip lit.':9} {'run_stats':10} "
      f"{'request_stats':14} {'pinned by'}")
print("-" * 118)
for key in all_keys:
    print(f"{key:26} {str(key in patch_keys):10} {str(key in tip_keys):9} "
          f"{str(key in run_keys):10} {str(key in req_keys):14} "
          f"{pinned.get(key, 'NOT PINNED')}")
print()
print(f"patch literal ({len(patch_keys)}): {patch_keys}")
print(f"tip whitelist ({len(tip_keys)}): {tip_keys}")
print(f"run_stats() at the tip ({len(run_keys)}): {run_keys}   | origin/main: {origin_keys}")
print(f"request_stats() ({len(req_keys)}): {req_keys}")
print(f"union of the two producers: {len(set(run_keys) | set(req_keys))}")
print()
print("reconciliation:")
print("  * the reviewer's 7-key literal is the PATCH's literal verbatim - the")
print("    round-5 N-3 print of the tip's whitelist is a superset of it, so the")
print("    two readings disagree about the MODULE, not about the patch.")
print("  * the tip's whitelist = patch literal + be_rows_rejected +")
print("    be_rows_rejected_reasons (commit c1538ca, 'receipt: keep the")
print("    row-refusal census the patch's whitelist dropped' - the round-2 §2.2")
print("    census restore).")
print("  * '5+3 -> 8' in N-3 is the producer union (run_stats 5 + request_stats 3),")
print("    not the whitelist length. The whitelist is a SUPERSET of that union by")
print("    exactly one key: be_fetches.")
print("  * be_fetches is IN the patch literal and in the tip's whitelist, and it")
print("    is produced by NOTHING in any revision: run_stats() at the tip, at the")
print("    patch's post-image and on origin/main never returns it; the only place")
print("    it appears in code is tests/test_capture_betexplorer.py's stub of")
print("    run_stats(), which is what the whitelist was copied from. It is dead")
print("    weight in the filter, not a lost counter - and it is pre-existing, so")
print("    this round neither added nor removed it.")
print()
print("verdict: whitelist at the tip = 9 keys; producers = 8 keys; the delta from")
print("the reviewer's 7 is the two census keys, and the census keys are the ones")
print("the round-2 §2.2 ruling required.")
PY
