#!/usr/bin/env bash
# A-2 before/after census, measured with the REAL old code rather than a
# reconstruction: the same census script is run against the parent commit's
# tree (before) and the working tree (after), so the only difference between
# the two runs is the identity layer itself.
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/a_census_before_after.sh [before-commit]
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BUNDLE="$REPO/handoff/round5_form_h2h_2026-10-12"
PY="$REPO/.venv/bin/python"
BEFORE="${1:-$(git -C "$REPO" rev-parse --short HEAD~1)}"
WT=/tmp/census_before

cd "$REPO"
rm -rf "$WT"
git worktree add --detach --quiet "$WT" "$BEFORE"
trap 'git worktree remove --force "$WT" >/dev/null 2>&1 || true' EXIT

{
  echo "=== A-2 census before/after, real code on both sides ==="
  echo "before commit: $(git rev-parse --short "$BEFORE")   after: working tree"
  echo "census: the 814 fixture sides of the settled registry, prior archive rows"
  echo "before each side's own kickoff date, and sides with >= 5 priors."
  echo "command ($(basename "$0")): a_census.py run once per tree"
  echo
  echo "\$ PYTHONPATH=$WT/src .venv/bin/python $BUNDLE/a_census.py"
  env PYTHONPATH="$WT/src" "$PY" "$BUNDLE/a_census.py"
  echo
  echo "\$ PYTHONPATH=src .venv/bin/python $BUNDLE/a_census.py"
  env PYTHONPATH="$REPO/src" "$PY" "$BUNDLE/a_census.py"
} 2>&1 | tee "$BUNDLE/a_census_worktree.txt"
