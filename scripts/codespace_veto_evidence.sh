#!/usr/bin/env bash
# Codespaces evidence run for the SKIPPED_VETO acca price-evidence gate.
#
#   bash scripts/codespace_veto_evidence.sh [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--ci-run RUN_ID|none]
#
# What it does
#   1. Refuses to run on a dirty tracked tree (the audit rewrites tracked files).
#   2. Creates a venv OUTSIDE the repo ($HOME/.edgefactory_audit_venv).
#   3. Optionally tries to download the CI artifacts of a run and reports any
#      warehouse data files (*.csv.gz) inside them. state_*.json files are capture
#      bookkeeping, not data, and are ignored. Nothing is copied into localdata.
#   4. Rebuilds localdata/warehouse.duckdb and reports which sources were skipped.
#      The run is labelled FULL only when no source was skipped.
#   5. Runs the settlement audit and prints every bucket: overall results, gate
#      labels (SCOUTINGSTATS_SOLE + BETEXPLORER_RESCUE) vs the rest, and every
#      odds band x price-evidence cell with implied hit rate and z-score. The full
#      table goes to band_evidence_all_buckets.csv in the output folder.
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
  DATA_FILES="$(find "$ART" -type f -name '*.csv.gz' 2>/dev/null | wc -l | tr -d ' ')"
  STATE_FILES="$(find "$ART" -type f -name 'state_*.json' 2>/dev/null | wc -l | tr -d ' ')"
  echo "warehouse data files (*.csv.gz) in artifacts: $DATA_FILES"
  echo "capture bookkeeping files (state_*.json, not data, ignored): $STATE_FILES"
  if [[ "$DATA_FILES" -gt 0 ]]; then
    find "$ART" -type f -name '*.csv.gz' | sed 's/^/  /'
  fi
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
echo "== 5. all-bucket price-evidence report ($WH_STATUS warehouse)"
"$PY" - "$OUT/picks_audit_rolling.json" "$WH_STATUS" "$SKIPPED" "$OUT" <<'PY'
import csv, json, sys

path, wh_status, skipped, out_dir = sys.argv[1:5]
d = json.load(open(path))
vd = d["veto_deep_dive"]
cells = vd.get("all_buckets_band_evidence", {})
GATE_LABELS = {"SCOUTINGSTATS_SOLE", "BETEXPLORER_RESCUE"}
GATE_BAND = "1.50-2.00"
FIELDS = ["bucket", "band", "evidence", "settled_picks", "wins", "hit_rate",
          "priced_picks", "implied_hit_rate", "z_vs_implied", "roi"]


def pct(x):
    return "n/a" if x is None else f"{x * 100:.1f}%"


def roi(x):
    return "n/a" if x is None else f"{x * 100:+.1f}%"


def z(x):
    return "n/a" if x is None else f"{x:+.2f}"


rows = []
for key, s in cells.items():
    bucket, band, evidence = key.split("|", 2)
    rows.append({"bucket": bucket, "band": band, "evidence": evidence,
                 **{k: s.get(k) for k in FIELDS[3:]}})
with open(f"{out_dir}/band_evidence_all_buckets.csv", "w", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=FIELDS)
    writer.writeheader()
    for r in rows:
        writer.writerow(r)


def pool(items):
    n = sum(r["settled_picks"] for r in items)
    wins = sum(r["wins"] for r in items)
    priced = sum(r["priced_picks"] for r in items)
    implied = sum((r["implied_hit_rate"] or 0) * r["priced_picks"] for r in items)
    roi_sum = sum((r["roi"] or 0) * r["priced_picks"] for r in items)
    return {"n": n, "hit": wins / n if n else None,
            "implied": implied / priced if priced else None,
            "roi": roi_sum / priced if priced else None}


print(f"warehouse: {wh_status}" + (f" (skipped: {skipped.strip() or 'none'})"))
print(f"window: {d.get('start')}..{d.get('end')}  settled={len(d.get('settled_ledger', []))} "
      f"pending={d.get('pending_result_picks')} rescheduled={d.get('rescheduled_result_picks')} "
      f"voided={d.get('voided_event_picks')} ambiguous={d.get('ambiguous_result_picks')}")
print()

print("A. Every bucket, overall:")
print(f"  {'bucket':32s} {'n':>5s} {'hit':>7s} {'roi':>8s}")
for name, s in sorted(d["by_bucket"].items()):
    print(f"  {name:32s} {s['settled_picks']:5d} {pct(s['hit_rate']):>7s} {roi(s['roi']):>8s}")
print()

buckets = sorted({r["bucket"] for r in rows})
print("B. Gate labels (SCOUTINGSTATS_SOLE + BETEXPLORER_RESCUE) vs the rest, per bucket:")
print(f"  {'bucket':32s} | {'all bands: gate n':>17s} {'hit':>6s} {'impl':>6s} {'roi':>7s}"
      f" | {'rest n':>6s} {'roi':>7s} | {GATE_BAND + ': gate n':>17s} {'hit':>6s} {'impl':>6s} {'roi':>7s} | {'rest n':>6s} {'roi':>7s}")
for b in buckets:
    all_rows = [r for r in rows if r["bucket"] == b]
    band_rows = [r for r in all_rows if r["band"] == GATE_BAND]
    g_all = pool([r for r in all_rows if r["evidence"] in GATE_LABELS])
    rest_all = pool([r for r in all_rows if r["evidence"] not in GATE_LABELS])
    g_band = pool([r for r in band_rows if r["evidence"] in GATE_LABELS])
    rest_band = pool([r for r in band_rows if r["evidence"] not in GATE_LABELS])
    print(f"  {b:32s} | {g_all['n']:17d} {pct(g_all['hit']):>6s} {pct(g_all['implied']):>6s} {roi(g_all['roi']):>7s}"
          f" | {rest_all['n']:6d} {roi(rest_all['roi']):>7s}"
          f" | {g_band['n']:17d} {pct(g_band['hit']):>6s} {pct(g_band['implied']):>6s} {roi(g_band['roi']):>7s}"
          f" | {rest_band['n']:6d} {roi(rest_band['roi']):>7s}")
print()

print(f"C. Every bucket, {GATE_BAND} band, every price-evidence label (full table: band_evidence_all_buckets.csv):")
print(f"  {'bucket|evidence':58s} {'n':>4s} {'hit':>7s} {'implied':>8s} {'z':>7s} {'roi':>8s}")
for r in rows:
    if r["band"] != GATE_BAND:
        continue
    print(f"  {r['bucket'] + '|' + r['evidence']:58s} {r['settled_picks']:4d} {pct(r['hit_rate']):>7s}"
          f" {pct(r['implied_hit_rate']):>8s} {z(r['z_vs_implied']):>7s} {roi(r['roi']):>8s}")
print()

print("D. SKIPPED_VETO trusted vs soft evidence:")
for name in ("trusted_evidence_only", "soft_evidence_only"):
    s = vd[name]
    print(f"  {name}: settled={s['settled_picks']} hit={pct(s['hit_rate'])} roi={roi(s['roi'])}")
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
