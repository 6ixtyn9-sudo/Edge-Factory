#!/usr/bin/env bash
# N-3 of the 2026-10-12 close-out: the four prints, taken AT THE CHAIN TIP and
# re-runnable from a clone.
#
#   (a) picks_today.py: the #61 rescue flow and BOTH stats calls, with lines
#   (b) betexplorer_odds.py: run_stats()/request_stats() field sets and their
#       union, the 13 marker counts, the five constants
#   (c) tests/test_betexplorer_politeness.py: both test sets, names and counts
#   (d) the per-file sha256 table at this tip and the attribution rows
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/n3_tip_prints.sh
set -uo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"
PY="$REPO/.venv/bin/python"
PYTHONPATH="$REPO/src" "$PY" - "$REPO" <<'PY'
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

repo = Path(sys.argv[1])


def lines(path, start, end):
    text = (repo / path).read_text().splitlines()
    for n in range(start, min(end, len(text)) + 1):
        print(f"{n:6d}  {text[n - 1]}")


def grep_n(pattern, path):
    out = subprocess.run(["grep", "-n", pattern, str(repo / path)],
                         capture_output=True, text=True).stdout
    return [l for l in out.splitlines() if l.strip()]


print("== (a) picks_today.py: the #61 rescue flow, both stats calls ==")
print("$ grep -n 'run_stats\\|request_stats\\|NETWORK-FREE SEAM\\|Bounded rescue' "
      "scripts/picks_today.py")
for line in grep_n(r"run_stats\|request_stats\|NETWORK-FREE SEAM\|Bounded rescue", "scripts/picks_today.py"):
    print("  " + line)
print()
print("the flow itself, numbered (scripts/picks_today.py):")
lines("scripts/picks_today.py", 6236, 6262)
print("      ... (step (2), step (3) and the two stats calls follow)")
lines("scripts/picks_today.py", 6275, 6291)
print()

print("== (b) betexplorer_odds.py: the two stat sets and the constants ==")
spec = importlib.util.spec_from_file_location(
    "be_odds", repo / "src/edgefactory/sources/betexplorer_odds.py")
be = importlib.util.module_from_spec(spec)
spec.loader.exec_module(be)
run_fields = sorted(be.run_stats())
req_fields = sorted(be.request_stats())
print(f"run_stats() fields ({len(run_fields)}): {', '.join(run_fields)}")
print(f"request_stats() fields ({len(req_fields)}): {', '.join(req_fields)}")
print(f"their union ({len(set(run_fields) | set(req_fields))}): "
      f"{', '.join(sorted(set(run_fields) | set(req_fields)))}")
print("the receipt whitelist in scripts/capture_betexplorer.py is a superset: "
      "it also carries be_fetches (from reset_fetch_count), so every field the "
      "two calls produce reaches the receipt")
text = (repo / "src/edgefactory/sources/betexplorer_odds.py").read_text()
markers = ["MARKETS", "DETAIL_MARKETS", "MARKET_TABS_ENABLED", "_MARKET_INTERVAL",
           "_MAX_REQUESTS_PER_RUN", "_MAX_MARKET_ROWS", "_MAX_MARKET_LINES",
           "parse_market_response", "fetch_market_responses",
           "fetch_match_odds_full", "request_stats", "_persist_match_detail",
           "_market_block"]
print(f"marker counts ({len(markers)} markers, occurrences and lines in the module):")
for m in markers:
    word = re.compile(rf"\b{re.escape(m)}\b")
    where = [n for n, line in enumerate(text.splitlines(), 1) if word.search(line)]
    shown = ", ".join(str(n) for n in where[:5]) + (" ..." if len(where) > 5 else "")
    print(f"  {m:24s} {len(word.findall(text)):4d} occurrence(s) at line(s) {shown}")
for const in ("_MARKET_INTERVAL", "_MAX_MARKET_ROWS", "_MAX_MARKET_LINES",
              "_MAX_H2H_ROWS", "_MAX_STANDINGS_ROWS"):
    print(f"  {const} = {getattr(be, const)!r}")
print()

print("== (c) the patch's two test modules: names and counts, collected at this tip ==")
for module in ("tests/test_betexplorer_politeness.py",
               "tests/test_betexplorer_match_detail.py"):
    out = subprocess.run(["env", f"PYTHONPATH={repo / 'src'}", str(repo / ".venv/bin/python"),
                          "-m", "pytest", module, "--collect-only", "-q",
                          "-p", "no:randomly"],
                         cwd=repo, capture_output=True, text=True).stdout
    names = [l.split("::", 1)[-1] for l in out.splitlines() if "::" in l]
    tail = [l for l in out.splitlines() if "test" in l and "::" not in l][-1:]
    print(f"-- {module}: {len(names)} test(s)")
    for n in names:
        print(f"   {n}")
    for t in tail:
        print(f"   ({t.strip()})")
print()

print("== (d) per-file sha256 at this tip + the attribution rows ==")
head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=repo,
                      capture_output=True, text=True).stdout.strip()
print(f"HEAD: {head}")
files = ["scripts/capture_betexplorer.py", "scripts/picks_today.py",
         "scripts/clean_localdata.py",
         "src/edgefactory/sources/betexplorer_match_snapshot.py",
         "src/edgefactory/sources/betexplorer_odds.py",
         "tests/test_betexplorer_match_detail.py",
         "tests/test_betexplorer_politeness.py",
         "docs/operator/BETEXPLORER-LICENSING.md", ".gitignore"]
for f in files:
    digest = hashlib.sha256((repo / f).read_bytes()).hexdigest()
    print(f"  {digest}  {f}")
print()
print("attribution rows (which commit of THIS chain carried each change in):")
chain = subprocess.run(
    ["git", "log", "--format=%h %s", "8e50de2..HEAD"], cwd=repo,
    capture_output=True, text=True).stdout.splitlines()
by_subject = {line.split(" ", 1)[1]: line.split(" ", 1)[0] for line in chain}
rows = [
    ("licensing doc Stage-1 consumption bullet",
     "pricing: the captured ledger reaches the board behind the flag"),
    ("capture receipt census whitelist",
     "receipt: keep the row-refusal census the patch's whitelist dropped"),
    ("picks_today rescue ordering / price index",
     "pricing: the captured ledger reaches the board behind the flag"),
    ("match_snapshot depth regions",
     "capture: the reviewer's record-depth patch, applied via git am -3 / "
     "capture: read the whole form block the page serves"),
    ("test_match_detail",
     "capture: the reviewer's record-depth patch, applied via git am -3 / "
     "receipt: keep the row-refusal census the patch's whitelist dropped"),
    ("odds adapter",
     "capture: the reviewer's record-depth patch, applied via git am -3"),
]
notes = {"odds adapter": " (both sides of the three contested hunks kept)"}
for change, subjects in rows:
    shas = [by_subject[s] for s in subjects.split(" / ") if s in by_subject]
    print(f"  {change:42s} <- {' + '.join(shas) if shas else 'NOT FOUND'}"
          f"{notes.get(change, '')}")
print()
print("(pre-reset SHAs are void: the whole chain was rebuilt after a sandbox reset,")
print(" so every attribution above cites this chain's own commits.)")
PY
