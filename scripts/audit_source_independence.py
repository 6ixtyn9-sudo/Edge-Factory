#!/usr/bin/env python3
"""Source-independence TR-1 triage audit (read-only).

Part of the source-strategy roadmap, phase 1 (triage): before adding any new
predictor source, answer for the LIVE consensus sources:

  1. Freshness — is each committed capture file still receiving rows
     (latest fixture date, rows in the last 7 days)?
  2. Independence — over the recent overlap window, do the sources say
     materially different things about the same fixtures, or do some mirror
     each other (correlated probs / lockstep picks)? A mirror gives the
     consensus the ILLUSION of three independent votes while moving it with
     one.
  3. Contribution — on fixtures all three cover, how often does dropping a
     source flip the mean-consensus pick? (Unweighted descriptive check; the
     production scheme is weighted.)

Data: committed capture files localdata/{forebet,zulubet,statarea}.csv.gz.
Vitibet and scoutingstats have no committed prob series in-repo (scoutingstats
capture went stale 2026-09-04 — see item-3 containment and its HANDOVER
addendum); they are reported as absent, not audited.

Run: `python3 scripts/audit_source_independence.py` (markdown to stdout).
"""
from __future__ import annotations

import csv
import gzip
import itertools
import math
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.util import norm_team  # noqa: E402

WINDOW_DAYS = 75
MIRROR_RULE = "corr>=0.98 & pick agreement>=99% & mean |gap| <=0.5pt -> mirror"
SOURCES = {"forebet": "forebet.csv.gz", "zulubet": "zulubet.csv.gz",
           "statarea": "statarea.csv.gz"}
SIDES = ("1", "X", "2")


def _load(path: Path, day_lo: str):
    probs: dict[tuple[str, str, str], tuple[float, float, float]] = {}
    latest = ""
    recent7_lo = (date.today() - timedelta(days=7)).isoformat()
    recent7 = 0
    with gzip.open(path, "rt", newline="") as fh:
        for row in csv.DictReader(fh):
            d = str(row.get("date") or "")[:10]
            if len(d) != 10 or d[4] != "-":
                continue
            latest = max(latest, d)
            if d >= recent7_lo:
                recent7 += 1
            if d < day_lo:
                continue
            try:
                vec = (float(row["p1"]), float(row["px"]), float(row["p2"]))
            except (TypeError, ValueError):
                continue
            probs[(d, norm_team(row.get("home") or ""),
                   norm_team(row.get("away") or ""))] = vec
    return probs, latest, recent7


def _pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    return cov / math.sqrt(vx * vy) if vx > 0 and vy > 0 else 0.0


def _argmax(vec):
    return max(range(3), key=lambda i: vec[i])


def main():
    today = date.today().isoformat()
    day_lo = (date.today() - timedelta(days=WINDOW_DAYS)).isoformat()
    data, meta = {}, {}
    for name, fname in SOURCES.items():
        probs, latest, recent7 = _load(ROOT / "localdata" / fname, day_lo)
        data[name] = probs
        meta[name] = (latest, recent7)
    # Audit the most recent window the files actually cover when the nominal
    # window is empty (committed captures all froze on 2026-06-12 — the load
    # pass keeps only >= day_lo rows, so reload on the shifted window).
    apex = max((m[0] for m in meta.values() if m[0]), default="")
    stale_banner = ""
    if not any(data.values()) and apex:
        day_lo = (date.fromisoformat(apex) - timedelta(days=WINDOW_DAYS)).isoformat()
        stale_banner = (f"\n> ⚠️ **All committed captures end {apex}.** Freshness is audited in "
                        f"section 1 against today; independence below is measured on the last "
                        f"covered window ({day_lo} → {apex}).\n")
        for name, fname in SOURCES.items():
            data[name], _, _ = _load(ROOT / "localdata" / fname, day_lo)
    print(f"# Source independence triage — generated {today}\n{stale_banner}")
    print("## 1. Freshness\n")
    print("| source | committed file | latest fixture date | rows last 7d | audited window fixtures |")
    print("|---|---|---|---|---|")
    for name, fname in SOURCES.items():
        latest, recent7 = meta[name]
        fresh = "✅" if latest >= (date.today() - timedelta(days=3)).isoformat() else "⚠️ stale"
        print(f"| {name} | {fname} | {latest} {fresh} | {recent7} | {len(data[name])} |")
    print("| vitibet | (no committed series) | — | — | — |")
    print("| scoutingstats | (no committed series; capture stale since 2026-09-04 — item 3 containment) | — | — | — |")

    print("\n## 2. Pairwise independence (window overlap)\n")
    print(f"Mirror rule: {MIRROR_RULE}.\n")
    print("| pair | shared fixtures | corr(p1,px,p2 flattened) | pick agreement | mean prob gap (first src's pick side) | verdict |")
    print("|---|---|---|---|---|---|")
    for a, b in itertools.combinations(SOURCES, 2):
        shared = set(data[a]) & set(data[b])
        va = [p for k in sorted(shared) for p in data[a][k]]
        vb = [p for k in sorted(shared) for p in data[b][k]]
        if not shared:
            print(f"| {a} vs {b} | 0 | – | – | – | no overlap |")
            continue
        corr = _pearson(va, vb)
        agree = sum(1 for k in shared if _argmax(data[a][k]) == _argmax(data[b][k])) / len(shared)
        gaps = [abs(data[a][k][_argmax(data[a][k])] - data[b][k][_argmax(data[a][k])])
                for k in shared]
        gap = sum(gaps) / len(gaps)
        mirror = corr >= 0.98 and agree >= 0.99 and gap <= 0.5
        heavy = corr >= 0.95 and agree >= 0.95
        verdict = "🚨 mirror" if mirror else ("⚠️ heavy co-signal" if heavy else "✅ distinct voice")
        print(f"| {a} vs {b} | {len(shared)} | {corr:.3f} | {agree * 100:.1f}% "
              f"| {gap:.2f} pts | {verdict} |")

    print("\n## 3. Contribution — pick flips when one source is dropped (triples)\n")
    triple = set.intersection(*(set(data[s]) for s in SOURCES))
    print(f"| shared across all three | {len(triple)} |")
    print("|---|---|")
    pick_full = {k: max(range(3), key=lambda i: sum(data[s][k][i]
                 for s in SOURCES) / 3) for k in triple}
    for s in SOURCES:
        rest = [x for x in SOURCES if x != s]
        flips = sum(1 for k in triple
                    if max(range(3), key=lambda i: sum(data[r][k][i] for r in rest) / 2) != pick_full[k])
        print(f"| drop {s} | {flips} flips ({100 * flips / max(1, len(triple)):.1f}%) |")


if __name__ == "__main__":
    main()
