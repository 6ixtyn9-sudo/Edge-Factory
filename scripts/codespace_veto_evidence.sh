#!/usr/bin/env bash
# Codespaces evidence run for the SKIPPED_VETO acca price-evidence gate.
#
#   bash scripts/codespace_veto_evidence.sh [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--ci-run RUN_ID|none]
#
# What it does
#   1. Refuses to run on a dirty tracked tree (the audit rewrites tracked files).
#   2. Creates a venv OUTSIDE the repo ($HOME/.edgefactory_audit_venv).
#   3. Optionally tries to download the CI artifacts of a run and reports which
#      missing warehouse sources appear inside them. Nothing is copied into localdata.
#   4. Rebuilds localdata/warehouse.duckdb and reports which sources were skipped.
#      The run is labelled FULL only when no source was skipped.
#   5. Runs the settlement audit and prints the SKIPPED_VETO cuts, including
#      band x price-evidence with implied hit rate and z-score, plus the pooled
#      gate slice (SCOUTINGSTATS_SOLE + BETEXPLORER_RESCUE in the 1.50-2.00 band).
#   6. Restores every tracked file the audit changed, so git status stays clean.
#
# Outputs go to $HOME/ef_audit_out/<timestamp>/ (run.log, audit json and md,
# build log). Nothing is committed, pushed, or sent to CI.

set -euo pipefail

START="2026-06-01"
END="2026-10-14"
CI_RUN="38717081638"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --start) START="$2"; shift 2 ;;
    --end) END="$2"; shift 2 ;;
    --ci-run) CI_RUN="$2"; shift 2 ;;
    -h|--help) sed -n '2,20p' "$0"; exit 0 ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || true)"
if [[ -z "$ROOT" || ! -f "$ROOT/scripts/audit_recent_picks.py" ]]; then
  echo "Run this from inside the Edge-Factory checkout." >&2
  exit 1
fi
cd "$ROOT"

if [[ -n "$(git status --porcelain --untracked-files=no)" ]]; then
  echo "Tracked files have local changes. Commit or stash them first:" >&2
  git status --short --untracked-files=no >&2
  exit 1
fi

TS="$(date +%Y%m%d-%H%M%S)"
OUT="$HOME/ef_audit_out/$TS"
mkdir -p "$OUT"
exec > >(tee -a "$OUT/run.log") 2>&1

echo "branch=$(git branch --show-current) head=$(git rev-parse --short HEAD)"
echo "window=$START..$END ci_run=$CI_RUN output=$OUT"

# ---- 1. environment (outside the repo) -------------------------------------
VENV="$HOME/.edgefactory_audit_venv"
if [[ ! -x "$VENV/bin/python" ]]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q --upgrade pip >/dev/null
"$VENV/bin/pip" install -q duckdb==1.5.6 pytest
if [[ -f requirements.txt ]]; then
  "$VENV/bin/pip" install -q -r requirements.txt
fi
PY="$VENV/bin/python"

# ---- 2. CI artifacts (report only) -----------------------------------------
echo
echo "== 2. CI artifacts for run $CI_RUN"
if [[ "$CI_RUN" == "none" ]]; then
  echo "skipped (--ci-run none)"
else
  ART="$OUT/ci_artifacts"
  mkdir -p "$ART"
  for name in "EdgeFactory-Reports" "Scored-Candidate-Audit-$CI_RUN"; do
    if gh run download "$CI_RUN" -R 6ixtyn9-sudo/Edge-Factory -n "$name" -D "$ART/$name" >/dev/null 2>&1; then
      echo "downloaded: $name"
    else
      echo "NOT downloaded: $name (gh auth, permissions, or network)"
    fi
  done
  FILES="$(find "$ART" -type f 2>/dev/null | wc -l | tr -d ' ')"
  echo "files in artifacts: $FILES"
  echo "missing warehouse sources found inside artifacts:"
  find "$ART" -type f 2>/dev/null \
    | grep -iE "vitibet|bettingclosed|prosoccer|bzzoiro|scoutingstats|predictz|betclan|freesupertips|afootballreport|windrawwin|soccervista|consensus4" \
    || echo "  (none)"
  echo "note: the CI localdata cache is not reachable from here; only artifacts are checked."
fi

# ---- 3. warehouse ------------------------------------------------------------
echo
echo "== 3. warehouse build"
"$PY" scripts/build_warehouse.py > "$OUT/build_warehouse.log" 2>&1
SKIPPED="$(grep -oE '^ +[a-z0-9_]+: skipped' "$OUT/build_warehouse.log" | sed -E 's/^ +//; s/: skipped//' | sort -u | tr '\n' ' ' || true)"
if [[ -z "${SKIPPED// /}" ]]; then
  WH_STATUS="FULL"
else
  WH_STATUS="PARTIAL"
fi
echo "warehouse status: $WH_STATUS"
echo "skipped sources: ${SKIPPED:-none}"
grep -E "warehouse built" "$OUT/build_warehouse.log" || true

# ---- 4. audit ----------------------------------------------------------------
echo
echo "== 4. settlement audit $START..$END"
"$PY" scripts/audit_recent_picks.py --warehouse localdata/warehouse.duckdb --start "$START" --end "$END" \
  > "$OUT/audit.log" 2>&1
cp localdata/picks_audit_rolling.json "$OUT/picks_audit_rolling.json"
cp "localdata/picks_audit_${END}.md" "$OUT/picks_audit_${END}.md" 2>/dev/null || true

# ---- 5. report ---------------------------------------------------------------
echo
echo "== 5. SKIPPED_VETO price-evidence report ($WH_STATUS warehouse)"
"$PY" - "$OUT/picks_audit_rolling.json" "$WH_STATUS" "$SKIPPED" <<'PY'
import json, math, sys

path, wh_status, skipped = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(path))
vd = d["veto_deep_dive"]
GATE_LABELS = ("SCOUTINGSTATS_SOLE", "BETEXPLORER_RESCUE")
GATE_BAND = "1.50-2.00"


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def roi(x):
    return "n/a" if x is None else f"{x * 100:+.1f}%"


def z(x):
    return "n/a" if x is None else f"{x:+.2f}"


print(f"warehouse: {wh_status}" + (f" (skipped: {skipped.strip() or 'none'})"))
print(f"window: {d.get('start')}..{d.get('end')}")
print(
    f"settled={d.get('settled_ledger') and len(d['settled_ledger'])} "
    f"pending={d.get('pending_result_picks')} rescheduled={d.get('rescheduled_result_picks')} "
    f"voided={d.get('voided_event_picks')} ambiguous={d.get('ambiguous_result_picks')}"
)
print()
ov = vd["overall"]
print(f"SKIPPED_VETO overall: settled={ov['settled_picks']} hit={pct(ov['hit_rate'])} roi={roi(ov['roi'])}")
for name in ("trusted_evidence_only", "soft_evidence_only"):
    s = vd[name]
    print(f"  {name}: settled={s['settled_picks']} hit={pct(s['hit_rate'])} roi={roi(s['roi'])}")
print()
print("by price evidence (SKIPPED_VETO):")
for k, s in vd["by_price_evidence"].items():
    print(f"  {k:24s} n={s['settled_picks']:4d} hit={pct(s['hit_rate']):>7s} roi={roi(s['roi']):>8s}")
print()


def table(title, cells):
    print(title)
    print(f"  {'band|evidence':50s} {'n':>4s} {'hit':>7s} {'implied':>8s} {'z':>7s} {'roi':>8s}")
    for k, s in cells.items():
        print(
            f"  {k:50s} {s['settled_picks']:4d} {pct(s['hit_rate']):>7s} "
            f"{pct(s['implied_hit_rate']):>8s} {z(s['z_vs_implied']):>7s} {roi(s['roi']):>8s}"
        )
    print()


table("SKIPPED_VETO band x evidence:", vd.get("band_x_evidence", {}))
table("CAUTION (contrast) band x evidence:", vd.get("contrast_band_x_evidence", {}))


def pool(cells, labels, band):
    rows = [
        (v, k) for k, v in cells.items()
        if k.split("|", 1)[0] == band and k.split("|", 1)[1] in labels
    ]
    n = sum(v["settled_picks"] for v, _ in rows)
    wins = sum(v["wins"] for v, _ in rows)
    priced = sum(v["priced_picks"] for v, _ in rows)
    implied_num = sum((v["implied_hit_rate"] or 0) * v["priced_picks"] for v, _ in rows)
    roi_num = sum((v["roi"] or 0) * v["priced_picks"] for v, _ in rows)
    return {
        "n": n,
        "hit": wins / n if n else None,
        "implied": implied_num / priced if priced else None,
        "roi": roi_num / priced if priced else None,
        "priced": priced,
    }


cells = vd.get("band_x_evidence", {})
gate = pool(cells, GATE_LABELS, GATE_BAND)
rest = {
    k: v for k, v in cells.items()
    if k.split("|", 1)[0] == GATE_BAND and k.split("|", 1)[1] not in GATE_LABELS
}
rest_pooled = pool({k: v for k, v in rest.items()}, set(x.split("|", 1)[1] for x in rest), GATE_BAND)
print(f"GATE SLICE (SKIPPED_VETO, {GATE_BAND}, labels {' + '.join(GATE_LABELS)}):")
print(
    f"  n={gate['n']} hit={pct(gate['hit'])} implied={pct(gate['implied'])} "
    f"roi={roi(gate['roi'])} (pooled; z not pooled)"
)
print(f"  everything else in {GATE_BAND}: n={rest_pooled['n']} hit={pct(rest_pooled['hit'])} "
      f"implied={pct(rest_pooled['implied'])} roi={roi(rest_pooled['roi'])}")
PY

# ---- 6. restore tracked files ------------------------------------------------
echo
echo "== 6. restoring tracked files the audit changed"
CHANGED="$(git status --porcelain --untracked-files=no | awk '{print $2}')"
if [[ -n "$CHANGED" ]]; then
  echo "$CHANGED"
  # shellcheck disable=SC2086
  git checkout -- $CHANGED
else
  echo "nothing to restore"
fi
echo "git status after restore:"
git status --short --untracked-files=no
echo
echo "done. Paste the section starting at '== 5.' or send $OUT/run.log"
