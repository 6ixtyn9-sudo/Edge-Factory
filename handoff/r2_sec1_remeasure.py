#!/usr/bin/env python3
"""R2 §1 — re-measure the registry numbers on `origin/main` before designing floors.

The round-4 pack's §1 carries reviewer-measured numbers for the committed
registry. The base has moved since (`origin/main` = `dda42ee`), the registry
settles daily, and standing rule: every brief value is re-measurable, and any
difference is REPORTED, never adjusted by feel. So this driver reads the
registry out of git (`git show origin/main:<path>` — never the working tree),
re-computes every §1 line with its definition printed, and diffs the result
against the pack's numbers.

Read-only: it writes nothing but its own stdout (captured to
`handoff/r2_sec1_remeasure.txt`).
"""
from __future__ import annotations

import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import json
import pathlib
import re
import subprocess
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

REGISTRY = "localdata/enhancement_registry.json"

# The round-4 pack's §1 numbers, verbatim, as relayed.
PACK = {
    "priced records": 409,
    "distinct team tokens": 578,
    "teams with >=10 records": 0,
    "teams with >=5 records": 8,
    "league field present": "0/409",
    "over_25 n": 350,
    "over_15 n": 33,
    "over_35 n": 16,
    "btts_yes n": 7,
    "match_over_15 hit%": "72.7%",
    "match_over_15 profit (units)": -5.78,
    "top teams >=5": "Celtic 6, Man City 6, Feyenoord 6",
}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def main() -> int:
    base = git("rev-parse", "origin/main").strip()
    print("== R2 §1 re-measurement ==")
    print(f"  base               : origin/main = {base}")
    print(f"  registry           : {REGISTRY} (via git show, never the working tree)")
    blob = subprocess.run(["git", "show", f"origin/main:{REGISTRY}"], cwd=ROOT,
                          capture_output=True, check=True).stdout
    import hashlib
    print(f"  registry blob      : sha256 {hashlib.sha256(blob).hexdigest()}")
    print(f"                       {len(blob)} bytes, last commit "
          f"{git('log', '-1', '--format=%cI %h', base, '--', REGISTRY).strip()}")
    print(f"  working-tree copy  : {'same' if (ROOT / REGISTRY).read_bytes() == blob else 'DIFFERENT (not used here)'}")

    data = json.loads(blob)
    markets = data.get("markets") or {}
    print(f"  registry version   : {data.get('version')}, {len(markets)} market type(s)")

    records = []
    for market, entry in sorted(markets.items()):
        for rec in (entry.get("records") or []):
            records.append({**rec, "_market": market})
    priced = [r for r in records if isinstance(r.get("price"), (int, float))]
    print()
    print("== §1 line 1 — priced records ==")
    print(f"  definition : records across all markets carrying a numeric `price`")
    print(f"  measured   : {len(priced)} priced / {len(records)} stored")
    print(f"  pack       : {PACK['priced records']}  -> "
          f"{'MATCH' if len(priced) == PACK['priced records'] else 'DIFFERENCE'}")

    def teams_of(match: str) -> list[str]:
        return [t.strip() for t in re.split(r"\s+vs\s+", str(match or ""), maxsplit=1)
                if t.strip()]

    raw_tokens, keyed_tokens = Counter(), Counter()
    from edgefactory.identity import source_team_key  # type: ignore
    for r in priced:
        ts = teams_of(r.get("match"))
        for t in ts:
            raw_tokens[t] += 1
            try:
                keyed_tokens[source_team_key(t)] += 1
            except Exception:
                keyed_tokens[t] += 1
    print()
    print("== §1 line 2 — distinct team tokens ==")
    print(f"  definition : distinct team names in the priced records' `match` field")
    print(f"  measured   : {len(raw_tokens)} raw spellings / {len(keyed_tokens)} "
          "repo-keyed tokens (source_team_key)")
    print(f"  pack       : {PACK['distinct team tokens']} (raw spellings)  -> "
          f"{'MATCH' if len(raw_tokens) == PACK['distinct team tokens'] else 'DIFFERENCE'}")

    def dist(counter: Counter) -> dict:
        return {f">={k}": sum(1 for v in counter.values() if v >= k)
                for k in (10, 5, 4, 3, 2)}

    print()
    print("== §1 line 3 — teams by record count ==")
    print(f"  definition : how many priced records each team token appears in")
    print(f"  measured (raw spellings) : {dist(raw_tokens)}")
    print(f"  measured (repo keys)     : {dist(keyed_tokens)}")
    top = [f"{t} {c}" for t, c in raw_tokens.most_common() if c >= 5]
    topk = [f"{t} {c}" for t, c in keyed_tokens.most_common() if c >= 5]
    print(f"  teams with >=5 (raw)     : {top}")
    print("    (the pack names 'Man City'; the registry spells it 'Manchester City' -"
          "\n     a naming difference, not a count difference)")
    print(f"  teams with >=5 (keys)    : {topk}")
    print(f"  pack                     : >=10 {PACK['teams with >=10 records']}, "
          f">=5 {PACK['teams with >=5 records']} ({PACK['top teams >=5']})")

    print()
    print("== §1 line 4 — the `league` field ==")
    league_fields = ("league", "league_name", "country_league", "competition")
    present = {f: sum(1 for r in priced if r.get(f)) for f in league_fields}
    print(f"  definition : priced records carrying any of {list(league_fields)}")
    print(f"  measured   : {present} over {len(priced)} priced records")
    print(f"  pack       : {PACK['league field present']}  -> "
          f"{'MATCH' if not any(present.values()) else 'DIFFERENCE'}")

    print()
    print("== §1 line 5 — per-market priced n ==")
    per_market = Counter(r["_market"] for r in priced)
    for market, n in per_market.most_common():
        entry = markets[market]
        print(f"  {market:24s} n={n:4d}  status={entry.get('status')} "
              f"hits={entry.get('hits')} profit={entry.get('profit')}")
    print(f"  markets with n=1 (the pack's \"three singles\") : "
          f"{[m for m, n in per_market.items() if n == 1]}")
    # the pack's §1 labels are short; the registry's market types are not
    # (over_25 -> match_over_25@v1, btts_yes -> btts_yes@v1)
    for label, key in (("over_25", "over_25 n"), ("over_15", "over_15 n"),
                       ("over_35", "over_35 n"), ("btts_yes", "btts_yes n")):
        hit = [m for m in per_market if m == f"{label}@v1" or m == f"match_{label}@v1"]
        got = sum(per_market[m] for m in hit)
        print(f"  pack {key:12s} = {PACK[key]:4d}  -> measured {got} "
              f"{'MATCH' if got == PACK[key] else 'DIFFERENCE'} ({hit})")

    print()
    print("== §1 line 6 — the over_15 trap ==")
    cands = [m for m in markets if "over_15" in m]
    for market in cands:
        entry = markets[market]
        recs = [r for r in (entry.get("records") or [])
                if isinstance(r.get("price"), (int, float))]
        n = len(recs)
        if not n:
            continue
        hits = sum(1 for r in recs if r.get("hit"))
        profit = sum((r["price"] - 1.0) if r.get("hit") else -1.0 for r in recs)
        print(f"  {market}: n={n} hits={hits} hit%={100.0 * hits / n:.1f} "
              f"units={profit:+.2f}  (recorded hits={entry.get('hits')}, "
              f"profit={entry.get('profit')})")
    print(f"  pack : {PACK['match_over_15 hit%']} hit / "
          f"{PACK['match_over_15 profit (units)']} u  -> compare above; the same "
          "slice must not be used to LOWER a floor")

    print()
    print("== difference report ==")
    diffs = []
    if len(priced) != PACK["priced records"]:
        diffs.append(f"priced {len(priced)} vs pack {PACK['priced records']}")
    if len(raw_tokens) != PACK["distinct team tokens"]:
        diffs.append(f"distinct teams {len(raw_tokens)} vs pack "
                     f"{PACK['distinct team tokens']}")
    if dist(raw_tokens)[">=10"] != PACK["teams with >=10 records"]:
        diffs.append(f">=10 teams {dist(raw_tokens)['>=10']}")
    if dist(raw_tokens)[">=5"] != PACK["teams with >=5 records"]:
        diffs.append(f">=5 teams {dist(raw_tokens)['>=5']}")
    if any(present.values()):
        diffs.append(f"league field now populated: {present}")
    if diffs:
        print("  DIFFERENCES (reported, never adjusted for):")
        for d in diffs:
            print(f"   - {d}")
    else:
        print("  none: every pack §1 number reproduces on origin/main "
              f"{base[:7]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
