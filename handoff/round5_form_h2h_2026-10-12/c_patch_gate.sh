#!/usr/bin/env bash
# C of the 2026-10-12 adjudication: the patch-transfer gate, re-printed at the
# current tip.
#
# Prints, for the reviewer's patch (handoff/betexplorer-depth.patch):
#   * its size and sha256, against the two figures on record;
#   * git apply --numstat, against the patch's own header;
#   * git apply -3 in a worktree at the chain's parent commit: which files
#     apply cleanly and which conflict (with the conflicted-hunk count);
#   * the per-file sha256 at the tip, at the parent, and at the patch's
#     post-image, with a verdict per file - and, where the tip differs from
#     the post-image, the commits that touched the file since (drift has to
#     be named, never smoothed over).
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/c_patch_gate.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BUNDLE="$REPO/handoff/round5_form_h2h_2026-10-12"
PATCH="$REPO/handoff/betexplorer-depth.patch"
PY="$REPO/.venv/bin/python"
BASE=8e50de2          # the chain's parent: where the patch was applied
                      # (the pre-reset 53c5a65 is void; the chain was rebuilt)
W=/tmp/c_patch_gate
FILES="
.gitignore
docs/operator/BETEXPLORER-LICENSING.md
scripts/capture_betexplorer.py
scripts/clean_localdata.py
scripts/picks_today.py
src/edgefactory/sources/betexplorer_match_snapshot.py
src/edgefactory/sources/betexplorer_odds.py
tests/test_betexplorer_match_detail.py
tests/test_betexplorer_politeness.py
"

cd "$REPO"
rm -rf "$W"
git worktree add --detach --quiet "$W" "$BASE"
trap 'git worktree remove --force "$W" >/dev/null 2>&1 || true' EXIT

{
  echo "=== C: patch-transfer gate at $(git rev-parse --short HEAD) ==="
  echo
  echo "\$ sha256sum handoff/betexplorer-depth.patch; wc -c -l handoff/betexplorer-depth.patch"
  sha256sum "$PATCH"
  wc -c -l "$PATCH"
  echo "  on record: edc6b09661f1... / 96,156 B / 1,908 lines (this file),"
  echo "  operator's figure: e685e1a1... / 96,155 B. The +1 B was never byte-"
  echo "  resolved (round-2 note); the patch is accepted on functional evidence."
  echo
  echo "\$ git -C $W apply --numstat handoff/betexplorer-depth.patch"
  git -C "$W" apply --numstat "$PATCH"
  echo
  echo "  patch header says: 9 files changed, 1597 insertions(+), 46 deletions(-)"
  echo
  echo "\$ git -C $W apply -3 handoff/betexplorer-depth.patch   # conflicts listed below"
  git -C "$W" apply -3 "$PATCH" || true
  echo
  echo "  conflicted files (status 'UU') and their hunk count:"
  git -C "$W" status --porcelain | grep '^UU' | awk '{print $2}' | while read -r f; do
    printf '    %s  (%s conflict hunk(s))\n' "$f" "$(grep -c '^<<<<<<<' "$W/$f" || true)"
  done
  echo
  echo "  files that applied CLEANLY:"
  for f in $FILES; do
    if git -C "$W" status --porcelain -- "$f" | grep -q '^UU'; then continue; fi
    if [ -f "$W/$f" ] || git -C "$W" status --porcelain -- "$f" | grep -q .; then
      echo "    $f"
    fi
  done
  echo
  echo "  NOTE (the memo's record vs this measurement): the round-5 adjudication"
  echo "  expected the conflict on scripts/picks_today.py. Measured here and in"
  echo "  the round-2 post-mortem: picks_today.py applies CLEANLY and the only"
  echo "  conflict is src/edgefactory/sources/betexplorer_odds.py (3 hunks, all"
  echo "  'both sides added'). No repair is attempted; the discrepancy is"
  echo "  reported as it stands."
  echo
  echo "== per-file sha256: tip / parent / patch post-image =="
  for f in $FILES; do
    tip_sha=$(git show "HEAD:$f" 2>/dev/null | sha256sum | cut -c1-64)
    raw_base=$(git show "$BASE:$f" 2>/dev/null || true)   # absent = added by the patch
    base_sha=$(printf '%s' "$raw_base" | sha256sum | cut -c1-64)
    post_sha=$(sha256sum "$W/$f" | cut -c1-64)
    since=$(git log --format='%h %s' --no-decorate "$BASE..HEAD" -- "$f" | paste -sd'; ' -)
    printf '  %s\n' "$f"
    printf '    tip        %s\n' "$tip_sha"
    if [ -n "$raw_base" ]; then
      printf '    parent     %s\n' "$base_sha"
    else
      printf '    parent     (absent: added by this patch)\n'
    fi
    printf '    post-image %s\n' "$post_sha"
    if git -C "$W" status --porcelain -- "$f" | grep -q '^UU'; then
      printf '    verdict    CONFLICTED - resolved by hand keeping both sides\n'
    elif [ "$tip_sha" = "$post_sha" ]; then
      printf '    verdict    IDENTICAL to the patch post-image'
      if [ "$tip_sha" != "$base_sha" ]; then printf ' (and changed by this patch)'; else printf ' (no change)'; fi
      printf '\n'
    else
      printf '    verdict    DIFFERS from the post-image - later commits touching it: %s\n' "${since:-none}"
    fi
  done
} 2>&1 | tee "$BUNDLE/c_patch_gate.txt"
