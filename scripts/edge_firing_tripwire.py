#!/usr/bin/env python3
"""edge_firing_tripwire.py — certified-edge & source-capture silence detector.

Surfaces two classes of SILENT failure the pipeline never reports as errors:

  1. CERTIFIED EDGE NOT FIRING — a certified rule with ZERO picks in the
     archived ledger over the last --edge-silent-days days. This would have
     caught the ML-meta 3-source bug (zero picks in every archive for weeks)
     and any future "edge exists but can never fire" regression.

  2. SOURCE CAPTURE STALE — a source whose newest captured row date is older
     than --source-stale-days days. This would have caught the betexplorer
     freeze of 2026-06-16 (starved results joins, kept a frozen combo
     "recent" in the edge table until the freshness gate landed).

WARN-only by design: silence can be legitimate (high thresholds, off-season,
retired sources). The tripwire never fails the pipeline — it makes silence
visible and persistent. Findings are printed and written to
localdata/edge_firing_tripwire.json (latest run; overwritten each run).

Usage:
    python3 scripts/edge_firing_tripwire.py
    python3 scripts/edge_firing_tripwire.py --edge-silent-days 21 --source-stale-days 7
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

# Active CSV sources (match refresh_result_sources.py + odds/ML sources).
# betexplorer deliberately ABSENT — capture retired 2026-06-16 (addendum 4);
# if it is ever revived, re-add it here and the tripwire guards it again.
SOURCES = (
    ("forebet", "date"),
    ("statarea", "date"),
    ("scoutingstats", "date"),
    ("vitibet", "date"),
    ("zulubet", "date"),
    ("predictz", "date"),
    ("windrawwin", "date"),
    ("afootballreport", "date"),
    ("betclan", "date"),
    ("freesupertips", "date"),
    ("bettingclosed", "date"),
    ("bzzoiro", "date"),
)

PICKS_GLOBS = ("picks_*.json", "picks_today.json", "picks_morning_*.json")


def _newest_source_date(ld: Path, name: str, date_col: str) -> tuple[str | None, str | None]:
    """Return (newest_row_date, newest_file) for a source, scanning only its
    newest monthly file (cheap — recent captures live in the newest file)."""
    files = sorted(ld.glob(f"{name}*.csv.gz"))
    if not files:
        return None, None
    newest = files[-1]
    max_date = None
    try:
        f = gzip.open(newest, "rt", encoding="utf-8", errors="replace")
        with f:
            import csv
            reader = csv.DictReader(f)
            for row in reader:
                d = str(row.get(date_col) or "")[:10]
                if len(d) == 10 and d.replace("-", "").isdigit():
                    if max_date is None or d > max_date:
                        max_date = d
    except OSError:
        return None, newest.name
    return max_date, newest.name


def _load_edge_rules(ld: Path) -> list[dict]:
    try:
        data = json.loads((ld / "edges_consensus.json").read_text())
    except (OSError, json.JSONDecodeError):
        return []
    return [e for e in data.get("edges", []) if e.get("status") == "certified"]


def _ml_ceiling_check(ld: Path, findings_edges: list[dict]) -> list[dict]:
    """Longer wire: a certified ml-meta edge whose live max ml_p is far below
    its certified threshold is structurally incapable of firing — a CEILING,
    distinct from mere silence. Uses the persisted ml_meta_state.json written
    by picks_today each run."""
    state_path = ld / "ml_meta_state.json"
    if not state_path.exists():
        return []
    try:
        state = json.loads(state_path.read_text())
    except (OSError, json.JSONDecodeError):
        return []
    max_p = state.get("max_ml_p")
    thresholds = state.get("thresholds") or []
    if max_p is None or not thresholds:
        return []
    min_thr = min(float(t) for t in thresholds)
    ceiling = []
    for f in findings_edges:
        if "ml-meta" not in f.get("rule", ""):
            continue
        if not f.get("silent"):
            continue
        gap = min_thr - max_p * 100.0
        if gap > 15.0:  # structurally far below the bar (>15pp gap)
            ceiling.append({
                "rule": f["rule"],
                "live_max_ml_p": round(max_p * 100.0, 1),
                "lowest_threshold": min_thr,
                "gap_pp": round(gap, 1),
                "ceiling": True,
            })
    return ceiling


def _scan_edge_firing(ld: Path, rules: list[dict], silent_days: int, today: date) -> list[dict]:
    """For each certified rule, count ledger picks in the last silent_days."""
    since = today  # any pick with date >= today - silent_days
    picks: list[dict] = []
    seen_files: set[Path] = set()
    for g in PICKS_GLOBS:
        for path in sorted(ld.glob(g)):
            if path in seen_files:
                continue
            seen_files.add(path)
            try:
                data = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(data, list):
                picks.extend(p for p in data if isinstance(p, dict))

    from datetime import timedelta
    cutoff = (today - timedelta(days=silent_days)).isoformat()
    findings = []
    for e in rules:
        rule = e.get("rule") or ""
        if not rule:
            continue
        decay = (e.get("decay") or {}).get("verdict")
        matched = [p for p in picks if (p.get("edge_rule") or p.get("rule")) == rule]
        in_window = [p for p in matched if str(p.get("date") or p.get("_archive_day") or "")[:10] >= cutoff]
        last = max((str(p.get("date") or p.get("_archive_day") or "")[:10] for p in matched), default=None)
        findings.append({
            "rule": rule,
            "decay": decay,
            "n_last_window": len(in_window),
            "last_fired": last,
            "silent": len(in_window) == 0,
        })
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="Certified-edge firing + source capture freshness tripwire")
    ap.add_argument("--edge-silent-days", type=int, default=14,
                    help="certified edge with zero ledger picks in this many days -> warn (default 14)")
    ap.add_argument("--source-stale-days", type=int, default=7,
                    help="source newest row older than this many days -> warn (default 7)")
    ap.add_argument("--localdata", default=str(LOCALDATA), help="localdata dir")
    args = ap.parse_args()

    ld = Path(args.localdata)
    today = date.today()
    findings: dict = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "edge_silent_days": args.edge_silent_days,
        "source_stale_days": args.source_stale_days,
        "edges": [],
        "sources": [],
    }

    # --- 1. certified-edge firing ---
    rules = _load_edge_rules(ld)
    edge_findings = _scan_edge_firing(ld, rules, args.edge_silent_days, today)
    findings["edges"] = edge_findings
    silent_edges = [f for f in edge_findings if f["silent"]]
    for f in sorted(edge_findings, key=lambda x: (x["silent"], x["rule"])):
        flag = "🔇 SILENT" if f["silent"] else "ok"
        print(f"  [{flag}] {f['rule']}  decay={f['decay']}  "
              f"fired_last_{args.edge_silent_days}d={f['n_last_window']}  last={f['last_fired'] or 'never'}")

    # --- 2. source capture freshness ---
    from datetime import timedelta
    stale_cutoff = (today - timedelta(days=args.source_stale_days)).isoformat()
    for name, date_col in SOURCES:
        newest_date, newest_file = _newest_source_date(ld, name, date_col)
        if newest_date is None:
            status = "no files" if newest_file is None else f"unreadable ({newest_file})"
            print(f"  [..] {name}: {status}")
            findings["sources"].append({"name": name, "newest_date": None,
                                        "newest_file": newest_file, "stale": None})
            continue
        stale = newest_date < stale_cutoff
        flag = "⚠️ STALE" if stale else "ok"
        print(f"  [{flag}] {name}: newest row {newest_date} (file {newest_file})")
        findings["sources"].append({"name": name, "newest_date": newest_date,
                                    "newest_file": newest_file, "stale": stale})

    n_silent = len(silent_edges)
    n_stale = sum(1 for s in findings["sources"] if s.get("stale"))
    ceilings = _ml_ceiling_check(ld, edge_findings)
    findings["ceilings"] = ceilings
    for c in ceilings:
        print(f"  [🔇 CEILED] {c['rule']}: live max ml_p {c['live_max_ml_p']:.1f}% vs "
              f"threshold {c['lowest_threshold']:.0f}% (gap {c['gap_pp']:.1f}pp) — "
              f"structurally cannot fire (unit mismatch or stale model).")
    n_ceil = len(ceilings)
    findings["warn_count"] = n_silent + n_stale + n_ceil
    out = ld / "edge_firing_tripwire.json"
    out.write_text(json.dumps(findings, indent=2, sort_keys=True))

    print(f"\n=== edge firing tripwire: {n_silent} silent edge(s), {n_ceil} ceiling(s), {n_stale} stale source(s) ===")
    if findings["warn_count"]:
        print("WARNINGS above are visibility only — the pipeline continues. "
              "Check whether each silence is expected (threshold/off-season/retired); "
              "a CEILING means the edge can never fire and needs a fix or decert.")
    print(f"full findings -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
