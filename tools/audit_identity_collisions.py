#!/usr/bin/env python3
"""READ-ONLY historical audit for the fixture-identity bug class.

Scans persisted artefacts (day pick archives, the scored-candidate shadow
ledger, the settled-result overlay, the purity/entity registries) for the
two failure directions:

  COLLISION  two different real teams sharing one key on one day
             (width-9 keys: "mancheste" covers Manchester City AND
             Manchester United);
  SPLIT      one real team carrying two keys (the Türkiye species):
             raw names that a curated alias links, or that are highly
             similar, yet key differently on the same day.

Mutates NOTHING. Writes a markdown report to --out (default stdout).

Usage:
    python tools/audit_identity_collisions.py [--root localdata] [--out report.md]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import canonical_team  # noqa: E402
from edgefactory.util import (  # noqa: E402
    canonical_team_key, char_ngram_similarity, is_degenerate_team_key,
    ledger_team_key, markers_conflict, norm_team, norm_team_legacy,
    resolve_team_alias,
)

SIMILARITY_FLOOR = 0.55

_GENERIC_NAME_TOKENS = frozenset({
    "fc", "cf", "sc", "ac", "cd", "ca", "club", "afc", "sk", "if", "fk",
    "bk", "ik", "ff", "ssc", "ks", "mfk", "nk", "hk", "us", "as",
})


def _name_tokens(name: str) -> list[str]:
    import re
    from edgefactory.util import _SQUAD_MARKERS, fold_ascii
    out = []
    for t in re.findall(r"[a-z0-9]+", fold_ascii(name)):
        if t in _GENERIC_NAME_TOKENS:
            continue
        # "B" and "II" are the same squad marker; normalize before compare
        out.append(_SQUAD_MARKERS.get(t, t))
    return out


def _truncation_of(a: str, b: str) -> bool:
    """One feed truncates the other ("Viktoria Plze" / "Viktoria Plzen")."""
    from edgefactory.util import compact_key
    ca, cb = compact_key(a), compact_key(b)
    if not ca or not cb or ca == cb:
        return ca == cb
    short, long_ = (ca, cb) if len(ca) <= len(cb) else (cb, ca)
    return len(short) >= 6 and long_.startswith(short)


def _prefix_linked(a: str, b: str) -> bool:
    """Same structural rule the live collapse uses (token prefix)."""
    ta, tb = _name_tokens(a), _name_tokens(b)
    if not ta or not tb:
        return False
    short, long_ = (ta, tb) if len(ta) <= len(tb) else (tb, ta)
    return long_[:len(short)] == short


def classify_collision(names: list[str]) -> str:
    """SUSPECT = the key unified names that are NOT one club."""
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if markers_conflict(a, b):
                return "SUSPECT"
            if resolve_team_alias(a)[0].lower() == resolve_team_alias(b)[0].lower():
                continue
            if not (_prefix_linked(a, b) or _truncation_of(a, b)):
                return "SUSPECT"
    return "benign"


def _iter_archive_rows(root: Path):
    for path in sorted(root.glob("picks_*.json")):
        try:
            rows = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            day = str(row.get("date") or path.stem.replace("picks_", ""))[:10]
            home, away = str(row.get("home") or ""), str(row.get("away") or "")
            if home and away:
                yield path.name, day, home, away


def _iter_settled_rows(root: Path):
    path = root / "settled_results.json"
    try:
        data = json.loads(path.read_text())
    except Exception:
        return
    for r in data.get("rows", []) if isinstance(data, dict) else []:
        home, away = str(r.get("home") or ""), str(r.get("away") or "")
        if home and away:
            yield path.name, str(r.get("date") or "")[:10], home, away


def scan(root: Path) -> dict:
    by_day_key: dict[tuple, set[str]] = defaultdict(set)
    by_day_names: dict[str, set[str]] = defaultdict(set)
    sources: dict[str, set[str]] = defaultdict(set)
    degenerate: set[str] = set()

    for src, day, home, away in list(_iter_archive_rows(root)) + list(_iter_settled_rows(root)):
        for name in (home, away):
            key = ledger_team_key(name)
            by_day_key[(day, key)].add(name)
            by_day_names[day].add(name)
            sources[name].add(src)
            if is_degenerate_team_key(canonical_team_key(name)):
                degenerate.add(name)

    collisions = []
    for (day, key), names in sorted(by_day_key.items()):
        if len(names) < 2:
            continue
        idents = {canonical_team(n) for n in names}
        if len(idents) == 1:
            continue
        ordered = sorted(names)
        collisions.append({"day": day, "key": key, "names": ordered,
                           "verdict": classify_collision(ordered)})

    splits = []
    for day, names in sorted(by_day_names.items()):
        # Blocking: only compare names that could plausibly be the same
        # team (shared 3-char prefix, or curated-alias siblings). A full
        # O(n^2) sweep over a season of slates does not terminate in
        # useful time and buys nothing — distinct prefixes are never
        # spelling variants of one name.
        blocks: dict[str, list[str]] = defaultdict(list)
        for name in sorted(names):
            folded = canonical_team_key(name, width=24)
            blocks[folded[:3]].append(name)
            blocks["alias:" + resolve_team_alias(name)[0].lower()].append(name)
        pairs = set()
        for group in blocks.values():
            for i, a in enumerate(group):
                for b in group[i + 1:]:
                    pairs.add((a, b) if a < b else (b, a))
        for a, b in sorted(pairs):
                if ledger_team_key(a) == ledger_team_key(b):
                    continue
                if markers_conflict(a, b):
                    continue
                alias_linked = (resolve_team_alias(a)[0].lower()
                                == resolve_team_alias(b)[0].lower())
                sim = char_ngram_similarity(a, b)
                if alias_linked or sim >= SIMILARITY_FLOOR:
                    splits.append({
                        "day": day, "a": a, "b": b,
                        "alias_linked": alias_linked, "similarity": round(sim, 2),
                        "keys": [ledger_team_key(a), ledger_team_key(b)],
                        "legacy": [norm_team_legacy(a), norm_team_legacy(b)],
                        "fixed": [norm_team(a), norm_team(b)],
                    })
    return {"collisions": collisions, "splits": splits,
            "degenerate": sorted(degenerate), "days": len(by_day_names)}


def render(result: dict) -> str:
    out = ["# Historical identity audit (read-only)", ""]
    out.append(f"Days scanned: {result['days']}  ")
    suspect = [c for c in result["collisions"] if c["verdict"] == "SUSPECT"]
    out.append(f"Collisions: {len(result['collisions'])} "
               f"(SUSPECT: {len(suspect)}, benign spelling variants: "
               f"{len(result['collisions']) - len(suspect)})  ")
    out.append(f"Split candidates: {len(result['splits'])}  ")
    out.append(f"Degenerate-key names: {len(result['degenerate'])}")
    out.append("")
    out.append("## Collisions (two real teams, one key, same day)")
    out.append("")
    if not result["collisions"]:
        out.append("_none_")
    for c in sorted(result["collisions"],
                    key=lambda c: (c["verdict"] != "SUSPECT", c["day"]))[:200]:
        out.append(f"* [{c['verdict']}] `{c['day']}` key=`{c['key']}` -> {c['names']}")
    out.append("")
    out.append("## Split candidates (one real team, two keys, same day)")
    out.append("")
    if not result["splits"]:
        out.append("_none_")
    for s in result["splits"][:200]:
        tag = "curated-alias" if s["alias_linked"] else f"sim={s['similarity']}"
        out.append(f"* `{s['day']}` {s['a']!r} vs {s['b']!r} ({tag}) "
                   f"keys={s['keys']} legacy={s['legacy']} fixed={s['fixed']}")
    out.append("")
    out.append("## Degenerate keys (identity unusable)")
    out.append("")
    out.append(", ".join(f"`{n}`" for n in result["degenerate"][:200]) or "_none_")
    out.append("")
    out.append("Read-only audit: no ledger, archive or registry was modified.")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(ROOT / "localdata"))
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    result = scan(Path(args.root))
    text = render(result)
    if args.out:
        Path(args.out).write_text(text)
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
