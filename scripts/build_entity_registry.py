#!/usr/bin/env python3
"""Build canonical league/team alias registry from captured localdata.

The registry is learned from evidence already in the cache:

- same loose event signature: date + loose_home_key + loose_away_key
- league team-pool overlap across labels
- small curated overrides in config/entity_overrides.json

Output:
    localdata/entity_registry.json

This is a context/reporting registry. It is safe to use for purity lookup and
picks metadata. Do not silently use it to change certified mining joins without
re-mining and validating.
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.entities import CONFIG_OVERRIDES_PATH, ENTITY_REGISTRY_PATH  # noqa: E402
from edgefactory.util import compact_key, norm_entity_team, norm_league  # noqa: E402

LOCALDATA = ROOT / "localdata"
SOURCE_RE = re.compile(r"^(.+)_\d{4}-\d{2}\.csv\.gz$")


class DSU:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra

    def groups(self) -> dict[str, list[str]]:
        out: dict[str, list[str]] = defaultdict(list)
        for x in list(self.parent):
            out[self.find(x)].append(x)
        return dict(out)


def source_from_path(path: Path) -> str:
    m = SOURCE_RE.match(path.name)
    return m.group(1) if m else path.name.split("_")[0]


def read_overrides() -> dict[str, Any]:
    try:
        data = json.loads(CONFIG_OVERRIDES_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def label_score(label: str, counts: Counter[str]) -> tuple[int, int, int, str]:
    text = str(label or "").strip()
    has_space = int(" " in norm_league(text))
    not_code = int(not re.fullmatch(r"[A-Za-z]{1,4}\d?", text.strip()))
    return (not_code, has_space, counts[text], text.lower())


def canonical_label(labels: list[str], counts: Counter[str], *, kind: str) -> str:
    if not labels:
        return "unknown"
    best = max(labels, key=lambda x: label_score(x, counts))
    return norm_league(best) if kind == "league" else norm_entity_team(best)


def add_alias_index(index: dict[str, str], raw: str, canonical: str, *, kind: str) -> None:
    if not raw:
        return
    index[raw] = canonical
    index[compact_key(raw)] = canonical
    if kind == "league":
        index[norm_league(raw)] = canonical
    else:
        index[norm_entity_team(raw)] = canonical


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="Build localdata/entity_registry.json from captured CSV cache")
    ap.add_argument("--min-team-overlap", type=float, default=0.65, help="League merge Jaccard threshold (default: 0.65)")
    ap.add_argument("--min-overlap-teams", type=int, default=8, help="Minimum shared teams for league overlap merge (default: 8)")
    ap.add_argument("--max-files", type=int, default=0, help="Debug: limit files read (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Print summary only, do not write registry")
    args = ap.parse_args()

    files = sorted(Path(p) for p in glob.glob(str(LOCALDATA / "*.csv.gz")))
    if args.max_files:
        files = files[: args.max_files]

    if not files:
        print("No localdata CSV cache files found; entity registry not built.")
        return

    league_dsu = DSU()
    team_dsu = DSU()
    league_counts: Counter[str] = Counter()
    team_counts: Counter[str] = Counter()
    league_sources: dict[str, set[str]] = defaultdict(set)
    team_sources: dict[str, set[str]] = defaultdict(set)
    league_team_sets: dict[str, set[str]] = defaultdict(set)
    event_leagues: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    event_homes: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    event_aways: dict[tuple[str, str, str], set[str]] = defaultdict(set)

    rows_seen = 0
    files_used = 0

    for path in files:
        source = source_from_path(path)
        try:
            df = pd.read_csv(path, dtype=str, usecols=lambda c: c in {"date", "home", "away", "league"})
        except Exception as exc:  # noqa: BLE001 - cache can contain heterogeneous files
            print(f"  WARN: skip {path.name}: {exc}")
            continue

        required = {"date", "home", "away"}
        if not required.issubset(df.columns):
            continue
        if "league" not in df.columns:
            df["league"] = "UNKNOWN"

        files_used += 1
        for row in df.itertuples(index=False):
            data = row._asdict()
            day = str(data.get("date") or "")[:10]
            home = str(data.get("home") or "").strip()
            away = str(data.get("away") or "").strip()
            league = str(data.get("league") or "UNKNOWN").strip() or "UNKNOWN"
            if not day or not home or not away:
                continue

            rows_seen += 1
            h_key = norm_entity_team(home)
            a_key = norm_entity_team(away)
            l_key = norm_league(league)
            loose_event = (day, norm_entity_team(home, width=24), norm_entity_team(away, width=24))

            league_dsu.find(l_key)
            team_dsu.find(h_key)
            team_dsu.find(a_key)

            league_counts[league] += 1
            team_counts[home] += 1
            team_counts[away] += 1
            league_sources[l_key].add(source)
            team_sources[h_key].add(source)
            team_sources[a_key].add(source)
            league_team_sets[l_key].update({h_key, a_key})

            event_leagues[loose_event].add(l_key)
            event_homes[loose_event].add(h_key)
            event_aways[loose_event].add(a_key)

    # Same loose event = same league/team entity aliases.
    same_event_merges = 0
    for labels in event_leagues.values():
        labels = list(labels)
        for other in labels[1:]:
            league_dsu.union(labels[0], other)
            same_event_merges += 1
    for labels in event_homes.values():
        labels = list(labels)
        for other in labels[1:]:
            team_dsu.union(labels[0], other)
    for labels in event_aways.values():
        labels = list(labels)
        for other in labels[1:]:
            team_dsu.union(labels[0], other)

    # League team-pool overlap catches aliases that did not share exact events.
    league_keys = list(league_team_sets)
    overlap_merges = 0
    for i, a in enumerate(league_keys):
        for b in league_keys[i + 1 :]:
            shared = len(league_team_sets[a] & league_team_sets[b])
            if shared < args.min_overlap_teams:
                continue
            sim = jaccard(league_team_sets[a], league_team_sets[b])
            if sim >= args.min_team_overlap:
                league_dsu.union(a, b)
                overlap_merges += 1

    # Curated overrides are authoritative.
    overrides = read_overrides()
    for raw, canon in (overrides.get("leagues", {}) or {}).items():
        league_dsu.union(norm_league(raw), norm_league(canon))
        league_counts[str(raw)] += 1
        league_counts[str(canon)] += 1
    for raw, canon in (overrides.get("teams", {}) or {}).items():
        team_dsu.union(norm_entity_team(raw), norm_entity_team(canon))
        team_counts[str(raw)] += 1
        team_counts[str(canon)] += 1

    league_groups = league_dsu.groups()
    team_groups = team_dsu.groups()

    league_alias_index: dict[str, str] = {}
    team_alias_index: dict[str, str] = {}
    leagues: dict[str, dict[str, Any]] = {}
    teams: dict[str, dict[str, Any]] = {}

    # Reverse raw labels to normalized keys for alias listing.
    raw_leagues_by_key: dict[str, set[str]] = defaultdict(set)
    raw_teams_by_key: dict[str, set[str]] = defaultdict(set)
    for raw in league_counts:
        raw_leagues_by_key[norm_league(raw)].add(raw)
    for raw in team_counts:
        raw_teams_by_key[norm_entity_team(raw)].add(raw)

    for _, keys in league_groups.items():
        raw_aliases = sorted({raw for key in keys for raw in raw_leagues_by_key.get(key, {key})})
        canonical = canonical_label(raw_aliases, league_counts, kind="league")
        sources = sorted({src for key in keys for src in league_sources.get(key, set())})
        teams_in_group = sorted({tm for key in keys for tm in league_team_sets.get(key, set())})
        leagues[canonical] = {
            "canonical": canonical,
            "display": max(raw_aliases, key=lambda x: label_score(x, league_counts)) if raw_aliases else canonical,
            "aliases": raw_aliases,
            "sources": sources,
            "team_count": len(teams_in_group),
            "evidence": {
                "alias_count": len(raw_aliases),
                "sources_count": len(sources),
            },
        }
        for raw in raw_aliases + keys:
            add_alias_index(league_alias_index, raw, canonical, kind="league")

    for _, keys in team_groups.items():
        raw_aliases = sorted({raw for key in keys for raw in raw_teams_by_key.get(key, {key})})
        canonical = canonical_label(raw_aliases, team_counts, kind="team")
        sources = sorted({src for key in keys for src in team_sources.get(key, set())})
        teams[canonical] = {
            "canonical": canonical,
            "display": max(raw_aliases, key=lambda x: label_score(x, team_counts)) if raw_aliases else canonical,
            "aliases": raw_aliases,
            "sources": sources,
            "evidence": {
                "alias_count": len(raw_aliases),
                "sources_count": len(sources),
            },
        }
        for raw in raw_aliases + keys:
            add_alias_index(team_alias_index, raw, canonical, kind="team")

    registry = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inputs": {
            "files_used": files_used,
            "rows_seen": rows_seen,
            "same_event_league_merges": same_event_merges,
            "team_overlap_league_merges": overlap_merges,
            "min_team_overlap": args.min_team_overlap,
            "min_overlap_teams": args.min_overlap_teams,
        },
        "alias_index": {
            "leagues": league_alias_index,
            "teams": team_alias_index,
        },
        "leagues": dict(sorted(leagues.items())),
        "teams": dict(sorted(teams.items())),
    }

    print("Entity registry build summary")
    print("=" * 60)
    print(f"files_used: {files_used}")
    print(f"rows_seen : {rows_seen}")
    print(f"leagues   : {len(leagues)} canonical, {len(league_alias_index)} aliases")
    print(f"teams     : {len(teams)} canonical, {len(team_alias_index)} aliases")
    print(f"merges    : same_event_league={same_event_merges}, league_team_overlap={overlap_merges}")

    if args.dry_run:
        print("--dry-run: registry NOT written")
        return

    ENTITY_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENTITY_REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True))
    print(f"wrote {ENTITY_REGISTRY_PATH}")


if __name__ == "__main__":
    main()
