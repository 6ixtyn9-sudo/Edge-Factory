#!/usr/bin/env bash
# W6 proof re-run for the round-5 bundle: the flag still gates the whole
# BetExplorer price attachment, and flag-off is byte-identical to the
# pre-stage-1 code (baseline) and to itself on the committed board's card.
#
# Run from the repository root:  bash handoff/round5_form_h2h_2026-10-12/w6_flag_gate_rerun.sh
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
BUNDLE="$REPO/handoff/round5_form_h2h_2026-10-12"
GATE="$REPO/handoff/flag_gate_2026-10-12"
W=/tmp/gate_r5
SHA="$(git -C "$REPO" rev-parse --short HEAD)"
PY="$REPO/.venv/bin/python"
# The baseline is the pre-stage-1 tree in a worktree. It is NOT optional: if
# the worktree is missing, PYTHONPATH falls through to the editable install
# and the "baseline" run silently becomes the current code compared with
# itself (found 2026-10-12 after a sandbox reset deleted /tmp). Hence the
# hard check, and the per-run edgefactory.__file__ line below.
BASE=${BASE:-/tmp/base_wt}
# The baseline is the stage-1 PRICING commit's parent. It is derived from
# the chain by subject, not hard-coded: the pre-reset SHA 9bd32e4 died with
# a sandbox reset, and a hard-coded SHA is exactly how a "baseline" run
# silently becomes the current code compared with itself.
PRICING_SUBJECT="pricing: the captured ledger reaches the board behind the flag"
PRICING_SHA=$(git -C "$REPO" log --format=%H --grep="^${PRICING_SUBJECT}$" -1)
if [ -z "$PRICING_SHA" ]; then
  echo "cannot find the stage-1 pricing commit in this branch; refusing to pick a baseline by guess" >&2
  exit 1
fi
BASE_COMMIT=${BASE_COMMIT:-$(git -C "$REPO" rev-parse --short "${PRICING_SHA}^")}
if [ ! -d "$BASE/src/edgefactory" ]; then
  echo "baseline worktree $BASE is missing; create it with:" >&2
  echo "  git worktree add --detach $BASE $BASE_COMMIT" >&2
  exit 1
fi

cd "$REPO"
rm -rf "$W"
mkdir -p "$W"
git archive HEAD localdata | tar -x -C "$W"
cp "$GATE/probe_board_picks.json" "$W/localdata/picks_probe_2026-10-12.json"

run() { echo "\$ $*"; "$@"; }

{
  echo "=== W6 flag-gate re-run at round-5 HEAD ($SHA) ==="
  echo "commands per handoff/flag_gate_2026-10-12/README.md, scratch root $W"
  echo "baseline = pre-stage-1 code (worktree $BASE @ $BASE_COMMIT = the parent of $PRICING_SHA,"
  echo "           this chain's stage-1 pricing commit, found by subject);"
  echo "off = current code, flag unset; on = current code, flag=1"
  echo "tree check:"
  echo "\$ PYTHONPATH=$BASE/src $PY -c 'import edgefactory; print(edgefactory.__file__)'"
  env PYTHONPATH="$BASE/src" "$PY" -c 'import edgefactory; print(edgefactory.__file__)'
  echo "\$ PYTHONPATH=src $PY -c 'import edgefactory; print(edgefactory.__file__)'"
  env PYTHONPATH=src "$PY" -c 'import edgefactory; print(edgefactory.__file__)'
  echo
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" ledger \
      --root "$W" --archived "$GATE/../live_2026-10-12"
  run env PYTHONPATH="$BASE/src" "$PY" "$GATE/prove_flag_gate.py" attach \
      --root "$W" --mode baseline --out "$W/board.baseline.json"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" attach \
      --root "$W" --mode off --out "$W/board.off.json"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" attach \
      --root "$W" --mode on --out "$W/board.on.json"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" slip \
      --board "$W/attached/picks_today.json.off.json" --scripts scripts --root "$W" \
      --out "$W/slip.today.off.txt"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" slip \
      --board "$W/attached/picks_today.json.on.json" --scripts scripts --root "$W" \
      --out "$W/slip.today.on.txt"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" slip \
      --board "$W/attached/picks_probe_2026-10-12.json.off.json" --scripts scripts --root "$W" \
      --out "$W/slip.probe.off.txt"
  run env PYTHONPATH=src "$PY" "$GATE/prove_flag_gate.py" slip \
      --board "$W/attached/picks_probe_2026-10-12.json.on.json" --scripts scripts --root "$W" \
      --out "$W/slip.probe.on.txt"
  echo
  echo "\$ sha256sum (freshly written ledger) and the round-2 committed ledger"
  sha256sum "$W/localdata/betexplorer_match_detail_2026-10-12.json" \
            "$GATE/ledger.betexplorer_match_detail_2026-10-12.json"
  echo "\$ diff <fresh ledger> <round-2 ledger>   # the only difference today"
  diff "$W/localdata/betexplorer_match_detail_2026-10-12.json" \
       "$GATE/ledger.betexplorer_match_detail_2026-10-12.json" || true
  echo

  compare() {
    local left=$1 right=$2 label=$3
    if cmp -s "$W/$left" "$W/$right"; then
      echo "\$ diff -q $left $right  ->  IDENTICAL   ($label)"
    else
      echo "\$ diff -q $left $right  ->  DIFFERS   ($label)"
      diff "$W/$left" "$W/$right" | head -20 || true
    fi
  }
  compare board.baseline.json board.off.json "flag off vs pre-stage-1"
  compare slip.today.off.txt slip.today.on.txt "committed board card off vs on"
  compare board.off.json board.on.json "flag on vs off (expected to differ)"
  compare slip.probe.off.txt slip.probe.on.txt "labelled probe card off vs on"

  echo
  echo "\$ diff board.off.json board.on.json | grep -c '^[<>]'   # content lines changed"
  diff "$W/board.off.json" "$W/board.on.json" | grep -c '^[<>]' || true
  echo "\$ diff board.off.json board.on.json | wc -l   # including hunk headers (the round-3 proof's metric)"
  diff "$W/board.off.json" "$W/board.on.json" | wc -l || true
  echo
  echo "\$ diff slip.probe.off.txt slip.probe.on.txt"
  diff "$W/slip.probe.off.txt" "$W/slip.probe.on.txt" || true
} 2>&1 | tee "$BUNDLE/w6_flag_gate_rerun.txt"
