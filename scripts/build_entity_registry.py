#!/usr/bin/env python3
"""Build canonical league/team alias registry from captured localdata.

The registry is learned from evidence already in the cache:

- same loose event signature: date + loose_home_key + loose_away_key
- Kickoff-and-Odds Aware Self-Learning Alias Engine
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

from edgefactory.entities import CONFIG_OVERRIDES_PATH, ENTITY_REGISTRY_PATH, classify_competition  # noqa: E402
from edgefactory.util import compact_key, norm_entity_team, norm_league  # noqa: E402

LOCALDATA = ROOT / "localdata"
SOURCE_RE = re.compile(r"^(.+)_\d{4}-\d{2}\.csv\.gz$")

GENERIC_LEAGUE_KEYS = {
    "unknown",
    "world friendlies clubs",
    "world club friendlies",
    "club friendlies",
    "international friendlies",
    "friendly",
    "friendlies",
    "premier league",
    "super league",
    "first league",
    "second league",
    "third league",
    "division 1",
    "division 2",
    "division 3",
    "first division",
    "second division",
    "third division",
    "league one",
    "league two",
    "serie a",
    "serie b",
    "liga 1",
    "liga 2",
}


def safe_league_alias_merge(a: str, b: str) -> bool:
    a_key = norm_league_cached(a)
    b_key = norm_league_cached(b)
    if not a_key or not b_key or a_key == b_key:
        return False
    if a_key in GENERIC_LEAGUE_KEYS or b_key in GENERIC_LEAGUE_KEYS:
        return False
    return classify_competition(a_key) == classify_competition(b_key)


def is_generic_league_label(raw: object) -> bool:
    return norm_league_cached(raw) in GENERIC_LEAGUE_KEYS


def canonical_league_label(labels: list[str], counts: Counter[str]) -> str:
    non_generic = [x for x in labels if not is_generic_league_label(x)]
    pool = non_generic or labels
    return canonical_label(pool, counts, kind="league")


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
    has_space = int(" " in norm_league_cached(text))
    not_code = int(not re.fullmatch(r"[A-Za-z]{1,4}\d?", text.strip()))
    return (not_code, has_space, counts[text], text.lower())


def canonical_label(labels: list[str], counts: Counter[str], *, kind: str) -> str:
    if not labels:
        return "unknown"
    best = max(labels, key=lambda x: label_score(x, counts))
    return norm_league_cached(best) if kind == "league" else norm_entity_team_cached(best)


def add_alias_index(index: dict[str, str], raw: str, canonical: str, *, kind: str) -> None:
    if not raw:
        return
    index[raw] = canonical
    index[compact_key(raw)] = canonical
    if kind == "league":
        index[norm_league_cached(raw)] = canonical
    else:
        index[norm_entity_team_cached(raw)] = canonical


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


# ----------------- Memoization Cache for High Performance -----------------

_TEAM_CACHE: dict[str, str] = {}
def norm_entity_team_cached(name: str) -> str:
    if name not in _TEAM_CACHE:
        _TEAM_CACHE[name] = norm_entity_team(name)
    return _TEAM_CACHE[name]


_LEAGUE_CACHE: dict[str, str] = {}
def norm_league_cached(name: str) -> str:
    if name not in _LEAGUE_CACHE:
        _LEAGUE_CACHE[name] = norm_league(name)
    return _LEAGUE_CACHE[name]


# ----------------- Kickoff-and-Odds Aware Self-Learning Alias Engine helpers -----------------

def parse_hhmm(val: Any) -> str | None:
    if pd.isna(val) or not val:
        return None
    val_s = str(val).strip()
    if " " in val_s:
        val_s = val_s.split(" ")[1]
    elif "T" in val_s:
        val_s = val_s.split("T")[1]
    if len(val_s) >= 5 and val_s[2] == ":":
        return val_s[:5]
    return None


def _safe_float(val: Any) -> float | None:
    if pd.isna(val) or not val:
        return None
    try:
        f = float(val)
        return f if f > 1.0 else None
    except Exception:
        return None


def char_ngram_similarity(s1: str, s2: str, n: int = 2) -> float:
    def get_ngrams(s: str) -> set[str]:
        clean = re.sub(r"[^a-z0-9]", "", s.lower())
        return {clean[i : i + n] for i in range(len(clean) - n + 1)} if len(clean) >= n else set()

    g1 = get_ngrams(s1)
    g2 = get_ngrams(s2)
    if not g1 or not g2:
        return 0.0
    return len(g1 & g2) / len(g1 | g2)


def check_event_match(m1: dict, m2: dict) -> bool:
    if not m1["hhmm"] or not m2["hhmm"]:
        return False

    h1, m_1 = map(int, m1["hhmm"].split(":"))
    h2, m_2 = map(int, m2["hhmm"].split(":"))
    mins1 = h1 * 60 + m_1
    mins2 = h2 * 60 + m_2

    diff = abs(mins1 - mins2) % 60
    time_match = diff <= 5 or diff >= 55
    if not time_match:
        return False

    odds_compared = 0
    odds_matching = 0
    for o_name in ["odd1", "oddx", "odd2"]:
        v1 = m1[o_name]
        v2 = m2[o_name]
        if v1 is not None and v2 is not None:
            odds_compared += 1
            if abs(v1 - v2) <= 0.05:
                odds_matching += 1
    odds_match = odds_compared >= 1 and odds_matching == odds_compared
    if not odds_match:
        return False

    ev1 = f"{m1['home']} {m1['away']}"
    ev2 = f"{m2['home']} {m2['away']}"
    sim = char_ngram_similarity(ev1, ev2, n=2)
    return sim >= 0.40


def check_league_match(l1: str, l2: str) -> bool:
    """Check if two league names can be considered aliases.

    Relies on the fact that the caller (the alias engine) already enforces
    check_event_match() — kickoff within 5min, odds within 0.05, team name
    bigram >= 0.40. If two sources sit on the exact same match with identical
    times and odds, their league labels MUST be aliases. No text similarity
    floor is needed on top of that gate.
    """
    k1 = norm_league_cached(l1)
    k2 = norm_league_cached(l2)
    if not k1 or not k2 or k1 == k2:
        return False

    # Safeguard 1: Do not align/merge generic keywords
    if k1 in GENERIC_LEAGUE_KEYS or k2 in GENERIC_LEAGUE_KEYS:
        return False

    # Safeguard 2: Enforce identical structural classification (no league-to-cup merges)
    if classify_competition(l1) != classify_competition(l2):
        return False

    # No text-similarity gate needed here. The caller (self-learning alias engine)
    # already enforces check_event_match() which requires kickoff, odds, and
    # team-name alignment. If two sources have the exact same match with the
    # same kickoff and same odds, the league labels are de facto aliases
    # regardless of surface-form similarity (e.g. "UCL" vs "Champions League").
    return True


def load_existing_registry_aliases(team_dsu: DSU, league_dsu: DSU) -> tuple[int, int]:
    if not ENTITY_REGISTRY_PATH.exists():
        return 0, 0
    try:
        data = json.loads(ENTITY_REGISTRY_PATH.read_text())
        loaded_teams = 0
        for canonical, info in data.get("teams", {}).items():
            aliases = info.get("aliases", [])
            for alias in aliases:
                team_dsu.union(norm_entity_team_cached(canonical), norm_entity_team_cached(alias))
                loaded_teams += 1
        loaded_leagues = 0
        for canonical, info in data.get("leagues", {}).items():
            aliases = info.get("aliases", [])
            for alias in aliases:
                league_dsu.union(norm_league_cached(canonical), norm_league_cached(alias))
                loaded_leagues += 1
        return loaded_teams, loaded_leagues
    except Exception:
        return 0, 0


def main() -> None:
    ap = argparse.ArgumentParser(description="Build localdata/entity_registry.json from captured CSV cache")
    ap.add_argument("--min-team-overlap", type=float, default=0.65, help="League merge Jaccard threshold (default: 0.65)")
    ap.add_argument("--min-overlap-teams", type=int, default=8, help="Minimum shared teams for league overlap merge (default: 8)")
    ap.add_argument("--max-files", type=int, default=0, help="Debug: limit files read (0 = all)")
    ap.add_argument("--dry-run", action="store_true", help="Print summary only, do not write registry")
    ap.add_argument("--full-scan", action="store_true", help="Scan all historical dates from scratch instead of active year only")
    args = ap.parse_args()

    files = sorted(Path(p) for p in glob.glob(str(LOCALDATA / "*.csv.gz")))
    files = [
        f
        for f in files
        if not any(
            x in f.name
            for x in ("betexplorer_results", "betexplorer_odds", "clv_snapshots", "purity_registry", "forecast")
        )
    ]
    if args.max_files:
        files = files[: args.max_files]

    if not files:
        print("No localdata CSV cache files found; entity registry not built.", flush=True)
        return

    league_dsu = DSU()
    team_dsu = DSU()
    
    pre_loaded_teams, pre_loaded_leagues = load_existing_registry_aliases(team_dsu, league_dsu)
    print(f"Pre-loaded {pre_loaded_teams:,} team and {pre_loaded_leagues:,} league aliases from the existing registry.", flush=True)

    league_counts: Counter[str] = Counter()
    team_counts: Counter[str] = Counter()
    league_sources: dict[str, set[str]] = defaultdict(set)
    team_sources: dict[str, set[str]] = defaultdict(set)
    league_team_sets: dict[str, set[str]] = defaultdict(set)
    event_leagues: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    all_matches_by_date: dict[str, list[dict]] = defaultdict(list)

    rows_seen = 0
    files_used = 0
    same_event_merges = 0
    overlap_merges = 0

    use_cols = ["date", "home", "away", "league", "kickoff", "time", "odd1", "oddx", "odd2"]
    quick_cols = ["date", "home", "away", "league"]

    print(f"Reading {len(files)} files to load teams and leagues...", flush=True)

    for idx, path in enumerate(files, 1):
        source = source_from_path(path)
        try:
            test_df = pd.read_csv(path, dtype=str, nrows=10)
            is_giant = len(test_df) >= 10 and "_" not in path.name
        except Exception:
            is_giant = False

        cols_to_load = quick_cols if is_giant else use_cols

        try:
            df = pd.read_csv(path, dtype=str, usecols=lambda c: c in cols_to_load)
            print(f"  [{idx}/{len(files)}] Loading {path.name}... ({len(df):,} rows, giant_mode={is_giant})", flush=True)
        except Exception as exc:
            print(f"  WARN: skip {path.name}: {exc}", flush=True)
            continue

        required = {"date", "home", "away"}
        if not required.issubset(df.columns):
            continue
        if "league" not in df.columns:
            df["league"] = "UNKNOWN"

        files_used += 1

        df['home'] = df['home'].fillna("").str.strip()
        df['away'] = df['away'].fillna("").str.strip()
        df['league'] = df['league'].fillna("UNKNOWN").str.strip()
        df['day'] = df['date'].fillna("").str[:10]
        
        df = df[(df['day'] != "") & (df['home'] != "") & (df['away'] != "")]
        if df.empty:
            continue

        unique_homes = df['home'].unique()
        home_map = {n: norm_entity_team_cached(n) for n in unique_homes}
        df['h_key'] = df['home'].map(home_map)

        unique_aways = df['away'].unique()
        away_map = {n: norm_entity_team_cached(n) for n in unique_aways}
        df['a_key'] = df['away'].map(away_map)

        unique_leagues = df['league'].unique()
        league_map = {n: norm_league_cached(n) for n in unique_leagues}
        df['l_key'] = df['league'].map(league_map)

        for h in df['h_key'].unique():
            team_dsu.find(h)
        for a in df['a_key'].unique():
            team_dsu.find(a)
        for l in df['l_key'].unique():
            league_dsu.find(l)

        for name, cnt in df['home'].value_counts().items():
            team_counts[name] += cnt
        for name, cnt in df['away'].value_counts().items():
            team_counts[name] += cnt
        for name, cnt in df['league'].value_counts().items():
            league_counts[name] += cnt

        for l in df['l_key'].unique():
            league_sources[l].add(source)
        for h in df['h_key'].unique():
            team_sources[h].add(source)
        for a in df['a_key'].unique():
            team_sources[a].add(source)

        for l_key, grp in df.groupby('l_key'):
            teams_in_league = set(grp['h_key'].unique()) | set(grp['a_key'].unique())
            league_team_sets[l_key].update(teams_in_league)

        dup_events = df[df.duplicated(subset=['day', 'h_key', 'a_key'], keep=False)]
        if not dup_events.empty:
            for (day, hk, ak), grp in dup_events.groupby(['day', 'h_key', 'a_key']):
                event_leagues[(day, hk, ak)].update(grp['l_key'].unique())
                homes = list(grp['h_key'].unique())
                for h in homes[1:]:
                    team_dsu.union(homes[0], h)
                aways = list(grp['a_key'].unique())
                for a in aways[1:]:
                    team_dsu.union(aways[0], a)

        rows_seen += len(df)

        if not is_giant:
            sub_df = df.copy()
            
            if 'kickoff' in sub_df.columns:
                ko_col = sub_df['kickoff']
            elif 'time' in sub_df.columns:
                ko_col = sub_df['time']
            else:
                ko_col = pd.Series([None] * len(sub_df), index=sub_df.index)
            
            sub_df['hhmm'] = ko_col.apply(parse_hhmm)
            sub_df['o1'] = sub_df['odd1'].apply(_safe_float) if 'odd1' in sub_df.columns else None
            sub_df['ox'] = sub_df['oddx'].apply(_safe_float) if 'oddx' in sub_df.columns else None
            sub_df['o2'] = sub_df['odd2'].apply(_safe_float) if 'odd2' in sub_df.columns else None

            sub_df = sub_df.dropna(subset=['hhmm'])
            sub_df = sub_df[sub_df['o1'].notna() | sub_df['ox'].notna() | sub_df['o2'].notna()]

            for row in sub_df.itertuples(index=False):
                data = row._asdict()
                all_matches_by_date[data['day']].append({
                    "source": source,
                    "home": data['home'],
                    "away": data['away'],
                    "league": data['league'],
                    "h_key": data['h_key'],
                    "a_key": data['a_key'],
                    "l_key": data['l_key'],
                    "hhmm": data['hhmm'],
                    "odd1": data['o1'],
                    "oddx": data['ox'],
                    "odd2": data['o2'],
                })

    # ----------------- Kickoff-and-Odds Aware Self-Learning Alias Engine -----------------
    scanner_merges = 0
    league_merges = 0
    scan_mode_label = "Full Scan Mode" if args.full_scan else "Incremental Mode: 2026+"
    print(f"\nRunning Kickoff-and-Odds Aware Self-Learning Alias Engine ({scan_mode_label})...", flush=True)
    all_dates_sorted = sorted(all_matches_by_date.items())
    for idx_day, (day, matches) in enumerate(all_dates_sorted, 1):
        if not args.full_scan and day < "2026-01-01":
            continue

        if idx_day % 50 == 0 or idx_day == len(all_dates_sorted):
            print(f"  Scanning date {day}... ({idx_day}/{len(all_dates_sorted)} dates, merged so far: teams={scanner_merges}, leagues={league_merges})", flush=True)

        by_min_mod = defaultdict(list)
        for m in matches:
            if m["hhmm"]:
                try:
                    h, mins = map(int, m["hhmm"].split(":"))
                    m_mod = (h * 60 + mins) % 60
                    by_min_mod[m_mod].append(m)
                except ValueError:
                    pass

        buckets = list(by_min_mod)
        n_buckets = len(buckets)
        for i in range(n_buckets):
            b1 = buckets[i]
            for j in range(i, n_buckets):
                b2 = buckets[j]
                dist = abs(b1 - b2)
                if dist > 30:
                    dist = 60 - dist
                if dist > 5:
                    continue

                for m1 in by_min_mod[b1]:
                    for m2 in by_min_mod[b2]:
                        if m1 is m2 or m1["source"] == m2["source"]:
                            continue
                        
                        # Compare events
                        if check_event_match(m1, m2):
                            # Union teams if they aren't already grouped
                            if team_dsu.find(m1["h_key"]) != team_dsu.find(m2["h_key"]) or team_dsu.find(m1["a_key"]) != team_dsu.find(m2["a_key"]):
                                team_dsu.union(m1["h_key"], m2["h_key"])
                                team_dsu.union(m1["a_key"], m2["a_key"])
                                scanner_merges += 1
                                
                            # Safe Jaccard mapping for leagues with strict safeguards (preventing cups/friendlies overlap)
                            if check_league_match(m1["league"], m2["league"]):
                                if league_dsu.find(m1["l_key"]) != league_dsu.find(m2["l_key"]):
                                    league_dsu.union(m1["l_key"], m2["l_key"])
                                    league_merges += 1

    print(f"Self-Learning Alias Engine completed! Merged {scanner_merges} team alignments and {league_merges} league alignments.", flush=True)

    league_groups = league_dsu.groups()
    team_groups = team_dsu.groups()

    league_alias_index: dict[str, str] = {}
    team_alias_index: dict[str, str] = {}
    leagues: dict[str, dict[str, Any]] = {}
    teams: dict[str, dict[str, Any]] = {}

    raw_leagues_by_key: dict[str, set[str]] = defaultdict(set)
    raw_teams_by_key: dict[str, set[str]] = defaultdict(set)
    for raw in league_counts:
        raw_leagues_by_key[norm_league_cached(raw)].add(raw)
    for raw in team_counts:
        raw_teams_by_key[norm_entity_team_cached(raw)].add(raw)

    print("\nGenerating final registry indexes...", flush=True)

    for _, keys in league_groups.items():
        raw_aliases = sorted({raw for key in keys for raw in raw_leagues_by_key.get(key, {key})})
        canonical = canonical_league_label(raw_aliases, league_counts)
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
            "self_learning_alias_merges": scanner_merges,
            "self_learning_league_merges": league_merges,
            "full_scan_completed": args.full_scan,
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
    print(f"merges    : same_event_league={same_event_merges}, league_team_overlap={overlap_merges}, self_learning_alias_merges={scanner_merges}, self_learning_league_merges={league_merges}")

    if args.dry_run:
        print("--dry-run: registry NOT written")
        return

    ENTITY_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ENTITY_REGISTRY_PATH.write_text(json.dumps(registry, indent=2, sort_keys=True))
    print(f"wrote {ENTITY_REGISTRY_PATH}")


if __name__ == "__main__":
    main()
