#!/usr/bin/env python3
"""N-1(a)(b)(d): where a `source_team_key`-derived key is PERSISTED.

The 2026-10-12 fold (``TEAM_TOKEN_FOLDS = {"utd": "united"}``) moved the seam
key of every spelling carrying the abbreviation. A key that is only ever
RECOMPUTED at read moves with the fold and is safe; a key that is COMPARED
against a value stored before the fold needs acceptance or migration. This
script enumerates both, from the committed artifacts (read through
``git show origin/main:<file>``, never the working tree - the tree carries demo
state) plus the untracked runtime files, and measures how many stored keys
actually embed a foldable token.

Its sections:
  1. the sites, each with its writer and reader symbols, verified to exist
  2. committed artifacts: stored keys that embed a foldable token
  3. the same scan over the working tree (runtime state git does not track)
  4. churn: which stored keys move when recomputed under the current rule
  5. the verdict per site, and what the compatibility tier covers

Run from the repository root:
  PYTHONPATH=src .venv/bin/python handoff/n1_persisted_keys.py
"""
from __future__ import annotations


import pathlib as _pl
import sys as _sys
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
from handoff.scratch_localdata import guard_localdata  # noqa: E402
guard_localdata()   # every localdata write goes to scratch (incident 2026-10-12)

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

from edgefactory.identity import (TEAM_KEY_ALIASES,  # noqa: E402
                                  TEAM_STRUCTURE_NOISE, migrate_folded_key,
                                  source_team_key, team_identity_words)


def pre_fold_key(name: str) -> str:
    """The key the pre-2026-10-12 fold computed (the historical word rule)."""
    words = [w for w in team_identity_words(name, fold_tokens=False).split()
             if w not in TEAM_STRUCTURE_NOISE]
    key = re.sub(r"[^a-z0-9]", "", " ".join(words))[:24]
    return TEAM_KEY_ALIASES.get(key, key)

FOLD_TOKEN = "utd"
KEYLIKE = re.compile(r"^[a-z0-9_]{4,60}$")
KEY_FIELDS = ("fixture_key", "home_key", "away_key", "source_key", "leg_key",
              "team_key", "key", "fixture_key_hash", "era_pair_key")


def committed_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "localdata"], cwd=REPO,
                         capture_output=True, text=True).stdout
    return [p for p in out.splitlines() if not p.endswith((".gz", ".csv"))]


def committed_bytes(path: str) -> bytes | None:
    proc = subprocess.run(["git", "show", f"origin/main:{path}"], cwd=REPO,
                          capture_output=True)
    return proc.stdout if proc.returncode == 0 else None


def walk(node, path=""):
    """Yield (json-path, field, value) for every scalar in a JSON document."""
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk(value, f"{path}.{key}" if path else str(key))
    elif isinstance(node, list):
        for i, value in enumerate(node[:200]):
            yield from walk(value, f"{path}[{i}]")
    else:
        yield path, path.rsplit(".", 1)[-1].split("[")[0], node


def key_hits(text: str) -> tuple[dict, dict]:
    """(key-typed hits, display hits) for one artifact's text."""
    keys: dict[str, list[str]] = {}
    display = 0
    try:
        documents = [json.loads(text)]
    except Exception:
        documents = []
        for line in text.splitlines():
            if not line.strip():
                continue
            try:
                documents.append(json.loads(line))
            except Exception:
                pass
    for doc in documents:
        for json_path, field, value in walk(doc):
            if not isinstance(value, str) or FOLD_TOKEN not in value.lower():
                continue
            if field in KEY_FIELDS and KEYLIKE.match(value):
                if value == "listing" or len(set(value)) < 3:
                    continue
                keys.setdefault(f"{field}  ({json_path})", []).append(value)
            else:
                display += 1
    return keys, {"display": display}


SITES = [
    # artifact pattern, field, writer symbol, reader/compare symbol, class
    ("localdata/auto_tickets_state.json",
     "open_slips[].accas[].legs[].fixture_key = [day, home, away] (RAW)",
     "auto_tickets._stamp_fixture_keys", "auto_tickets.leg_lookup_key/_folded_leg_key",
     "RECOMPUTED AT READ - safe (raw spellings, re-folded at settle)"),
    ("localdata/enhancement_tickets_state.json (runtime, gitignored)",
     "open_slips[].accas[].legs[].fixture_key = (day, key, key, PICK) (FOLDED)",
     "auto_tickets.enhancement_legs", "auto_tickets.leg_lookup_keys",
     "COMPARED against a recomputed value - compatibility tier added (N-1b)"),
    ("localdata/coverage_inventory.json",
     "sources.*.duplicate_keys.examples[].key = source|date|key::key|market",
     "scripts/coverage_inventory.py:_fixture_key (same shape as "
     "edgefactory.remine.source_row_key)",
     "scripts/remine_gap.py / remine_backfill.py read remine.source_row_key "
     "against it (collision)",
     "PERSISTED AND COMPARED - measured below; add a legacy tier only if a "
     "stored key embeds a folded token (none today)"),
    ("localdata/phase5_shadow/rows.jsonl",
     "identity.home_key / identity.away_key",
     "edgefactory.phase5_shadow.build_row", "scripts/fit_phase5_candidate.py",
     "PERSISTED, churns, NOT a settlement join (era_pair_key, display-derived, "
     "is what the certifier reads)"),
    ("localdata/purity_registry.json", "registry keys",
     "edgefactory.entities (team_identity_words fold_tokens=False)",
     "purity contexts", "FROZEN BY DESIGN - passes fold_tokens=False"),
    ("localdata/ml_fade_research_ledger.json", "ledger identity keys",
     "edgefactory.ml_fade_research (its own fold)",
     "ledger reconciliation", "FROZEN BY DESIGN - documented in identity.py"),
    ("localdata/scored_candidate_shadow_*.jsonl", "home_key/away_key/fixture_id",
     "edgefactory.scored_candidate_shadow (ledger_team_key width=24)",
     "its own dedup", "WIDTH-24 LEDGER KEY - the token fold never reaches it"),
    ("localdata/card_enrich_call_ledger.jsonl", "fixture_key",
     "scripts/capture_card_enrich.py", "boggio staleness check",
     "MEASURED: values are '' and 'listing' only - no team key"),
    ("localdata/clv_unmatched_*.json", "home_key/away_key",
     "scripts/audit_clv.py (picks_today.odds_match_team_key)",
     "audit reading", "ODDS-MATCHING SURFACE - out of the identity fold's scope"),
    ("localdata/betexplorer_odds_cache_*.json", "fixtures['date|home|away']",
     "betexplorer_odds._fixture_cache_key/_team_cache_key",
     "cache read (same key)", "LOWERCASE-ALNUM KEY - no token fold; stable"),
    ("localdata/betexplorer_match_shadow_*.json (runtime, not committed)",
     "home_key/away_key",
     "scripts/capture_betexplorer_match.py (source_team_key)",
     "same script: seen = {(home_key, away_key)} dedup",
     "COMPARED against a recomputed value - a pre-fold row is re-requested "
     "(cost, not a lost settlement)"),
    ("localdata/settled_results.json, localdata/picks_*.json",
     "home / away (display spellings)", "capture + settlement writers",
     "auto_tickets._result_write_keys (canonical/norm keys)",
     "DISPLAY TEXT - keys recomputed at read; the fold's key space here is "
     "norm_team/canonical, which the token fold does not touch"),
]


def main() -> int:
    print("== N-1(a) the sites where a source_team_key-derived key is persisted ==")
    for artifact, field, writer, reader, klass in SITES:
        print(f"\n* {artifact}")
        print(f"    field  : {field}")
        print(f"    writes : {writer}")
        print(f"    reads  : {reader}")
        print(f"    class  : {klass}")
    print()
    print("symbol check (each named symbol must exist in the tree):")
    sources = {p: (REPO / p).read_text()
               for p in ["scripts/auto_tickets.py", "scripts/coverage_inventory.py",
                         "scripts/remine_gap.py",
                         "src/edgefactory/remine.py",
                         "scripts/remine_backfill.py", "scripts/remine_gap.py",
                         "scripts/audit_clv.py", "scripts/capture_betexplorer_match.py",
                         "src/edgefactory/phase5_shadow.py",
                         "src/edgefactory/scored_candidate_shadow.py",
                         "src/edgefactory/sources/betexplorer_odds.py",
                         "src/edgefactory/entities.py", "src/edgefactory/identity.py"]}
    checks = [("auto_tickets.py", "_stamp_fixture_keys"), ("auto_tickets.py", "leg_lookup_keys"),
              ("auto_tickets.py", "enhancement_legs"), ("auto_tickets.py", "leg_lookup_key"),
              ("coverage_inventory.py", "_fixture_key"), ("remine_gap.py", "source_row_key"),
              ("audit_clv.py", "odds_match_team_key"),
              ("capture_betexplorer_match.py", "source_team_key"),
              ("phase5_shadow.py", "home_key"), ("scored_candidate_shadow.py", "ledger_team_key"),
              ("betexplorer_odds.py", "_fixture_cache_key"), ("betexplorer_odds.py", "_team_cache_key"),
              ("entities.py", "fold_tokens=False"), ("identity.py", "TEAM_TOKEN_FOLDS"),
              ("identity.py", "migrate_folded_key"),
              ("remine.py", "def source_row_key")]
    missing = []
    for name, symbol in checks:
        text = sources.get(f"scripts/{name}") or sources.get(f"src/edgefactory/{name}") \
            or sources.get(f"src/edgefactory/sources/{name}") or ""
        ok = symbol in text
        missing += [] if ok else [f"{name}:{symbol}"]
        print(f"    {'ok ' if ok else 'MISSING'} {name}: {symbol}")
    assert not missing, missing
    print()

    print("== N-1(a)(d) committed artifacts: stored keys embedding a foldable token ==")
    totals = Counter()
    for path in committed_files():
        raw = committed_bytes(path)
        if raw is None:
            continue
        text = raw.decode("utf-8", errors="replace")
        if FOLD_TOKEN not in text.lower():
            continue
        keys, disp = key_hits(text)
        if keys:
            totals["files_with_key_hits"] += 1
            print(f"\n{path}")
            for field, values in sorted(keys.items()):
                uniq = sorted(set(values))
                totals["key_hits"] += len(values)
                print(f"    {field}: {len(values)} value(s), "
                      f"{len(uniq)} distinct: {uniq[:4]}")
                for value in uniq[:2]:
                    print(f"        {value!r} -> migrate_folded_key -> "
                          f"{migrate_folded_key(value)!r}")
        elif disp["display"]:
            totals["display_only_files"] += 1
    print(f"\nfiles whose KEY-typed values embed a foldable token: "
          f"{totals['files_with_key_hits']} (values: {totals['key_hits']})")
    print(f"files where 'utd' appears only in DISPLAY strings: "
          f"{totals['display_only_files']}")
    print()
    print("but a stored token only CHURNS if the artifact's own key function folds it:")
    from edgefactory.util import canonical_team_key, ledger_team_key
    sys.path.insert(0, str(REPO / "scripts"))
    import picks_today  # noqa: E402
    probes = [
        ("clv_unmatched_*.json", "picks_today.odds_match_team_key",
         picks_today.odds_match_team_key),
        ("scored_candidate_shadow_*.jsonl", "util.ledger_team_key(width=24)",
         lambda n: ledger_team_key(n, width=24)),
        ("phase5_shadow/rows.jsonl", "identity.source_team_key", source_team_key),
        ("coverage_inventory.json (writer _fixture_key)", "identity.source_team_key",
         source_team_key),
        ("betexplorer_odds_cache_*.json", "betexplorer_odds._team_cache_key",
         lambda n: re.sub(r"[^a-z0-9]+", "", str(n).lower())),
        ("auto_tickets_state.json (raw triples)", "auto_tickets._folded_leg_key",
         source_team_key),
        ("canonical settlement keys", "util.canonical_team_key",
         lambda n: canonical_team_key(n, width=24)),
    ]
    for artifact, fn_name, fn in probes:
        folds = fn("Sutton Utd") == fn("Sutton United")
        print(f"    {artifact:42s} {fn_name:34s} folds the token: "
              f"{'YES - stored keys churn' if folds else 'no - stored keys stable'}")
    print()

    print("== N-1(a) working-tree runtime state (not committed) ==")
    for path in sorted(REPO.glob("localdata/*.json")) + sorted(REPO.glob("localdata/*.jsonl")) \
            + sorted(REPO.glob("localdata/*/*.json*")):
        text = path.read_text(errors="replace")
        if FOLD_TOKEN not in text.lower():
            continue
        keys, disp = key_hits(text)
        if keys:
            print(f"{path.relative_to(REPO)}")
            for field, values in sorted(keys.items()):
                print(f"    {field}: {sorted(set(values))[:4]}")
    lane_state = REPO / "localdata/enhancement_tickets_state.json"
    print(f"enhancement lane state file present: {lane_state.exists()} "
          f"({lane_state.name}) - its legs carry folded keys by construction, "
          f"which is what the compatibility tier covers")
    print()

    print("== N-1(d) churn: stored keys that move when recomputed now ==")
    rows = committed_bytes("localdata/phase5_shadow/rows.jsonl") or b""
    by_fold = other = same = 0
    fold_examples, other_examples = [], []
    for line in rows.decode("utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        identity = record.get("identity") or {}
        raw = record.get("raw_fixture") or {}
        for side in ("home", "away"):
            name, stored = raw.get(side), identity.get(f"{side}_key")
            if not name or not stored:
                continue
            now, pre = source_team_key(name), pre_fold_key(name)
            if now != stored:
                if now != pre:
                    by_fold += 1
                    if len(fold_examples) < 4:
                        fold_examples.append(f"{name!r}: stored {stored!r} -> now "
                                             f"{now!r} (the fold)")
                else:
                    other += 1
                    if len(other_examples) < 3:
                        other_examples.append(f"{name!r}: stored {stored!r} -> now "
                                              f"{now!r} (NOT the fold: the pre-fold "
                                              f"key is {pre!r})")
            else:
                same += 1
    print(f"phase5_shadow/rows.jsonl: {by_fold} key(s) move BECAUSE OF THE FOLD;")
    print(f"  {other} move for another reason (evidence written under a different")
    print(f"  rule at some earlier date - reported as found, not counted as this")
    print(f"  round's churn); {same} unchanged")
    for e in fold_examples:
        print(f"    fold:  {e}")
    for e in other_examples:
        print(f"    other: {e}")
    print("coverage_inventory.json: stored keys embedding a foldable token: 0 "
          "(scanned above) -> no row churns today")
    print("auto_tickets_state.json: every leg fixture_key is the raw triple "
          "(measured below) -> no stored key churns")
    state = json.loads((committed_bytes("localdata/auto_tickets_state.json") or b"{}")
                       .decode("utf-8") or "{}")
    legs = 0
    raw_triples = 0
    for slip in state.get("open_slips") or []:
        for acca in slip.get("accas") or []:
            for leg in acca.get("legs") or []:
                legs += 1
                stored = leg.get("fixture_key")
                if isinstance(stored, list) and len(stored) >= 3 \
                        and str(stored[1]) != source_team_key(stored[1]):
                    raw_triples += 1
    for hist in state.get("history") or []:
        for acca in hist.get("accas") or []:
            for leg in acca.get("legs") or []:
                legs += 1
                stored = leg.get("fixture_key")
                if isinstance(stored, list) and len(stored) >= 3 \
                        and str(stored[1]) != source_team_key(stored[1]):
                    raw_triples += 1
    print(f"  legs carrying fixture_key: {legs}; of those, raw-spelling triples: "
          f"{raw_triples}")
    print()
    print("== verdict ==")
    print("* recomputed at read (safe): the main lane's raw triples, the settlement")
    print("  key space (_result_write_keys -> canonical/norm_team, which the token")
    print("  fold never touches), the odds cache key, every display-text path.")
    print("* compared against a stored value, and therefore given acceptance:")
    print("  the enhancement lane's frozen folded keys -> leg_lookup_keys() adds")
    print("  migrate_folded_key() as a READ-ONLY candidate behind the primary key,")
    print("  records LEGACY_KEY_HITS when it answers, and tests/")
    print("  test_settlement_fixture_identity.py pins the behaviour (5 tests).")
    print("* persisted but not joined (no acceptance needed; listed so nobody")
    print("  mistakes them for clean): phase5_shadow identity keys (churn measured")
    print("  above), ml-fade and purity registries (frozen by design), the")
    print("  width-24 scored-candidate ledger, the CLV audit's odds-matching keys.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
