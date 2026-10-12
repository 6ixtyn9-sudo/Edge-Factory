#!/usr/bin/env bash
# Re-run the W3 coverage and W5 signal reports under the width-9 rule, for the
# comparison the round-5 bundle carries: what the same measurement says if the
# seam key is the width-9 norm_team bucket instead of the canonical
# source_team_key (the historical reading).
#
# The driver is run from a scratch copy whose identity.source_team_key is
# swapped, so the canonical outputs in this directory are untouched; the two
# width-9 outputs are written beside them as *_width9_rule.txt.
#
# Run from the repository root:
#   bash handoff/round5_form_h2h_2026-10-12/w35_width9_rule.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BUNDLE="$REPO/handoff/round5_form_h2h_2026-10-12"
PY="$REPO/.venv/bin/python"
W=/tmp/w9_rule

rm -rf "$W"
mkdir -p "$W"
cp -r "$REPO/src" "$W/src"
cp "$BUNDLE/intel_report.py" "$W/intel_report.py"
# the driver reads `localdata` and `Config` relative to the tree it runs in,
# and it puts its own "src" first on sys.path - so it MUST be run from the
# scratch root, with those two linked in. (Found 2026-10-12: running it from
# the repository root silently measured the canonical code under the width-9
# label, because sys.path.insert(0, "src") outranks PYTHONPATH.)
ln -s "$REPO/localdata" "$W/localdata"
ln -s "$REPO/Config" "$W/Config"

"$PY" - "$W/src/edgefactory/identity.py" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = '''def source_team_key(name: object) -> str:
    """Identity-folded voter-row team key with alias resolution."""
    key = source_team_key_base(name)
    return TEAM_KEY_ALIASES.get(key, key)'''
new = '''def source_team_key(name: object) -> str:
    """SCRATCH COPY: the width-9 rule (norm_team) instead of the seam key."""
    from .util import norm_team

    return norm_team(str(name or ""), width=9)'''
assert text.count(old) == 1, "scratch patch target moved"
path.write_text(text.replace(old, new), encoding="utf-8")
PY

{
  echo "=== W3/W5 under the width-9 rule (scratch tree $W) ==="
  echo "the seam key replaced by norm_team(name, width=9); everything else identical"
  echo
  echo "\$ (cd $W && PYTHONPATH=$W/src $PY $W/intel_report.py)"
  (cd "$W" && PYTHONPATH="$W/src" "$PY" "$W/intel_report.py")
  echo
  echo "\$ write the header, then the scratch outputs -> *_width9_rule.txt"
  header="comparison run: the same driver with the identity read as the width-9
norm_team bucket (scratch tree $W, patched at import: source_team_key =
norm_team(name, width=9)), every other change of this round held constant.
Reproduce with handoff/round5_form_h2h_2026-10-12/w35_width9_rule.sh (it
copies src/ and this bundle's intel_report.py to a scratch root, links
localdata and Config into it, swaps the key, and runs it from that root -
the driver puts its own src first on sys.path, so the working directory
decides which tree is measured)."
  for pair in "w3_coverage" "w5_signal"; do
    { printf '%s\n' "$header"; cat "$W/${pair}.txt"; } > "$BUNDLE/${pair}_width9_rule.txt"
  done
  head -7 "$BUNDLE/w3_coverage_width9_rule.txt"
} 2>&1 | tee "$BUNDLE/w35_width9_rule_run.txt"
