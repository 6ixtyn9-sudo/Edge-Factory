#!/usr/bin/env python3
"""Read-only name audit: does an odds fixture find its own result on its date?

For each (date, home, away) odds fixture with results on that date, classify
the match under the form key (``identity.source_team_key``, truncation map
included) and report the unmatched ones:

  matched          a result on the date pairs the same two clubs (either
                   orientation, so a home/away swap in the archive counts)
  name_variant     a result on the date pairs two names that are the same
                   clubs spelled differently (similar text on BOTH sides)
  partner_differs  one side has a result on the date, against another opponent
  no_result_row    nothing on the date involves either club

Read-only: prints a summary; writes nothing.

Usage:  PYTHONPATH=src python3 scripts/name_audit.py [--localdata DIR]
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
import sys
from collections import Counter, defaultdict
from difflib import SequenceMatcher
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from edgefactory.form_intel import load_archive  # noqa: E402
from edgefactory.identity import fold_identity_words, source_team_key  # noqa: E402

NAME_VARIANT_RATIO = 0.6


def same_club_key(a: str, b: str, key_of) -> bool:
    return key_of(a) == key_of(b)


def name_similar(a: str, b: str) -> bool:
    fa, fb = fold_identity_words(a), fold_identity_words(b)
    if not fa or not fb:
        return False
    if fa.startswith(fb) or fb.startswith(fa):
        return True
    return SequenceMatcher(None, fa, fb).ratio() >= NAME_VARIANT_RATIO


def classify(home: str, away: str, results: list[tuple[str, str]], key_of=source_team_key) -> str:
    """Classify one odds fixture against the (home, away) results on its date."""
    hk, ak = key_of(home), key_of(away)
    involved = False
    variant = False
    for rh, ra in results:
        pair_keys = {key_of(rh), key_of(ra)}
        if {hk, ak} == pair_keys or (hk == key_of(rh) and ak == key_of(ra)) \
                or (hk == key_of(ra) and ak == key_of(rh)):
            return "matched"
        if name_similar(home, rh) and name_similar(away, ra) \
                or name_similar(home, ra) and name_similar(away, rh):
            variant = True
        if hk in pair_keys or ak in pair_keys:
            involved = True
    if variant:
        return "name_variant"
    if involved:
        return "partner_differs"
    return "no_result_row"


def audit(odds: list[tuple[str, str, str]], results: dict[str, list[tuple[str, str]]],
          key_of=source_team_key) -> tuple[Counter, list]:
    counts: Counter = Counter()
    examples: dict[str, list] = defaultdict(list)
    for day, home, away in odds:
        cls = classify(home, away, results.get(day, []), key_of)
        counts[cls] += 1
        if cls != "matched" and len(examples[cls]) < 10:
            examples[cls].append((day, home, away))
    return counts, examples


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--localdata", default=str(REPO / "localdata"))
    args = ap.parse_args(argv)
    root = Path(args.localdata)

    odds: set[tuple[str, str, str]] = set()
    for fn in sorted(root.glob("theoddsapi_odds_2026-*.csv.gz")):
        with gzip.open(fn, "rt", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("market") == "ou_2.5":
                    odds.add((r["date"], r["home"], r["away"]))
    archive = load_archive(root)
    results: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for row in archive.rows:
        results[row["date"]].append((row["home"], row["away"]))
    days = {d for d, _, _ in odds if d in results}
    scoped = sorted(f for f in odds if f[0] in days)
    counts, examples = audit(scoped, results, key_of=archive._key)
    total = len(scoped)
    print(f"odds fixtures with results on their date: {total}")
    for cls in ("matched", "name_variant", "partner_differs", "no_result_row"):
        print(f"  {cls:16s} {counts.get(cls, 0):4d}  ({100 * counts.get(cls, 0) / max(total, 1):.1f}%)")
    for cls in ("name_variant", "partner_differs"):
        if examples.get(cls):
            print(f"examples: {cls}")
            for e in examples[cls]:
                print("   ", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
