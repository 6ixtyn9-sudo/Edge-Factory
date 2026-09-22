"""Replay-measurement harness for the identity fold (2026-09-22).

Analysis-only: reads archived pick slates and the purity registry and
reports what the identity fold changes. It mutates NOTHING and must NOT
be wired into any live generation path.

Metrics:
1. DUPLICATE MERGE: archived (date, home, away) groups that have >=2
   distinct raw spellings collapsing under team_identity_words — the
   duplicate class the fold kills (post-amendment source_team_key).
2. LEAGUE RESOLUTION: distinct archived league labels vs the purity
   registry's league keyspace — how many UNKNOWNs become RESOLVED through
   fold+alias, and the zero-no-change invariant on legacy-clean labels.
"""

from __future__ import annotations

import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import (
    _override_lookup,
    _registry_lookup,
    canonical_league,
)
from edgefactory.identity import team_identity_words
from edgefactory.util import norm_league


def legacy_canonical_league(label: str) -> str:
    """Pre-amendment canonical_league: exact logic that shipped before
    the identity-fold commit (override/registry hit, norm_league(raw)
    fallback)."""
    hit = _override_lookup("leagues", label) or _registry_lookup("leagues", label)
    if hit:
        return norm_league(str(hit))
    return norm_league(label)


def _load_archives() -> list[dict]:
    rows: list[dict] = []
    for path in sorted(glob.glob(str(ROOT / "localdata" / "picks_2026-*.json"))):
        try:
            data = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError):
            data = None
        if not data:
            continue
        if isinstance(data, dict):
            data = data.get("rows", data.get("picks", []))
        day = path.rsplit("picks_", 1)[-1][:10]
        for row in data:
            if str(row.get("date") or "")[:10] != day:
                continue
            rows.append(row)
    return rows


def main() -> int:
    rows = _load_archives()
    print(f"archived pick rows (same-day): {len(rows)}")

    # 1) duplicate-merge measurement
    raw_keys: dict[tuple, set] = defaultdict(set)
    for row in rows:
        key = (
            row.get("date"),
            team_identity_words(row.get("home") or ""),
            team_identity_words(row.get("away") or ""),
        )
        raw_keys[key].add((row.get("home") or "", row.get("away") or ""))
    dups = {k: v for k, v in raw_keys.items() if len(v) > 1}
    print(f"folded fixture identities with >1 raw spelling: {len(dups)}")
    for (date, home, away), raws in sorted(dups.items()):
        print(f"  {date} :: {sorted(raws)} -> ({home!r}, {away!r})")

    # 2) league resolution vs registry keyspace
    reg = json.loads((ROOT / "localdata" / "purity_registry.json").read_text())
    league_keys = {
        k.split("|")[1] for k in (reg.get("contexts", {}).get("league", {})) if "|" in k
    }
    labels = sorted({str(r.get("league") or "") for r in rows if r.get("league")})
    gains = []
    regressions = []
    preserved = 0
    for label in labels:
        old = legacy_canonical_league(label)
        new = canonical_league(label)
        old_resolved = old in league_keys
        if old_resolved and new != old:
            regressions.append((label, old, new))
        elif old == new:
            preserved += 1
        elif new in league_keys:
            gains.append((label, old, new))
    print(f"labels whose canonical is UNCHANGED: {preserved}")
    print(f"labels whose canonical changed: {len(gains)}")
    for label, old, new in gains:
        print(f"  {label!r}: {old!r} -> {new!r}")
    print(f"REGRESSIONS (previously-resolved, canonical moved): {len(regressions)}")
    for label, old, new in regressions:
        print(f"  {label!r}: {old!r} -> {new!r}")
    unknown_after = [
        l for l in labels
        if legacy_canonical_league(l) not in league_keys
        and canonical_league(l) not in league_keys
    ]
    print(f"still UNKNOWN after fold: {len(unknown_after)}"
          f"{' (sample: ' + ', '.join(unknown_after[:8]) + ')' if unknown_after else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
