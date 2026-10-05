#!/usr/bin/env python3
"""CLI smoke for cross-spelling fixture identity + duplicate collapse.

Checks, on controlled in-memory fixture data (no network, no localdata
writes), that two spellings of ONE real fixture resolve to one identity:

  * key derivation for both spellings (alias application is visible);
  * operational collapse: ONE surviving pick, one ``duplicate_fixture``
    rejection for the twin;
  * shadow identity: one fixture_id / candidate_id for the pair;
  * settlement grading a pick captured under spelling A from a result
    recorded under spelling B;
  * the near-duplicate tripwire staying silent when a curated alias
    already joined the pair, and firing (merging nothing) when no alias
    can join two genuinely different fixtures.

Provenance: the 2026-10-05 "Italy vs Türkiye" / "Italy vs Turkey" split
(diacritic deletion in norm_team + missing exonym alias). That pair is
the first CASE below; add a row to CASES for any further spelling family
worth guarding — the checks are generic.

Usage:  python tools/smoke_fixture_identity_dedupe.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.scored_candidate_shadow import (  # noqa: E402
    candidate_id, fixture_id, settle_candidate)
from edgefactory.util import canonical_team_key, explain_team_key  # noqa: E402

# (label, home, away spelling A, away spelling B)
CASES: list[tuple[str, str, str, str]] = [
    ("exonym/diacritic (2026-10-05)", "Italy", "Türkiye", "Turkey"),
    ("exonym (national-team rename)", "Poland", "Czechia", "Czech Republic"),
]

# A pair that no curated alias can (or should) join: the tripwire must fire
# and nothing may be merged.
UNJOINABLE = ("Italy", "Greece", "Portugal")


def _load_picks_today():
    spec = importlib.util.spec_from_file_location(
        "picks_today_smoke", ROOT / "scripts" / "picks_today.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _pick(home, away, odds, kickoff, avg_p, source, n):
    return {
        "date": "2026-10-05", "home": home, "away": away,
        "match": f"{home} vs {away}", "league": "World Cup",
        "market": "1x2", "pick": "home", "selection_side": "home",
        "odds": odds, "kickoff": kickoff, "avg_p": avg_p,
        "odds_source": source, "bucket": "CERTIFIED_CLEAN",
        "statistical_comment": f"n={n}", "w_score": 1.0,
    }


def _check_case(pt, label: str, home: str, away_a: str, away_b: str) -> bool:
    print(f"\n### case: {label} — {home} vs {away_a!r} / {away_b!r}")

    print("  -- key derivation --")
    for name in (away_a, away_b):
        print("   ", json.dumps(explain_team_key(name), ensure_ascii=False))

    rows = [
        _pick(home, away_a, 1.42, "05-10, 19:45", 0.70, "zulubet", 900),
        _pick(home, away_b, 1.47, "14:45", 0.64, "betexplorer", 1810),
    ]
    ident = {pt.canonical_fixture_identity(r) for r in rows}
    print("  -- canonical fixture identity --")
    print("    identities:", ident)

    collapsed, removed = pt.collapse_final_operational_picks(rows)
    print("  -- operational collapse --")
    print("    surviving:", len(collapsed), "| collapsed twins:", removed,
          "| twin rejection:", "duplicate_fixture" if removed else "NONE")

    same_fixture = (fixture_id(rows[0], "2026-10-05")
                    == fixture_id(rows[1], "2026-10-05"))
    same_candidate = (candidate_id(rows[0], "2026-10-05")
                      == candidate_id(rows[1], "2026-10-05"))
    print("  -- shadow identity --")
    print("    fixture_id equal:", same_fixture,
          "| candidate_id equal:", same_candidate)

    print("  -- tripwire (alias resolved -> must be silent) --")
    fired = pt.print_near_duplicate_fixture_tripwire(
        collapsed, day="2026-10-05", stream=sys.stdout)
    print("    warnings:", fired)

    settled = {("2026-10-05", canonical_team_key(home),
                canonical_team_key(away_b)): "home"}
    out = settle_candidate({"market": "1x2", "selection_side": "home",
                            "home_team": home, "away_team": away_a,
                            "trading_date": "2026-10-05"}, settled)
    print("  -- settlement across spellings --")
    print(f"    result as {away_b!r} grades pick as {away_a!r}:", out)

    ok = (len(ident) == 1 and len(collapsed) == 1 and removed == 1
          and same_fixture and same_candidate and fired == 0
          and out["settlement_status"] == "win")
    print("  case:", "PASS" if ok else "FAIL")
    return ok


def _check_unjoinable(pt) -> bool:
    home, away_a, away_b = UNJOINABLE
    print(f"\n### case: no alias available — {home} vs {away_a} / {away_b}")
    rows = [
        _pick(home, away_a, 1.42, "05-10, 19:45", 0.70, "zulubet", 900),
        _pick(home, away_b, 1.47, "05-10, 19:45", 0.64, "betexplorer", 900),
    ]
    kept, merged = pt.collapse_final_operational_picks(rows)
    fired = pt.print_near_duplicate_fixture_tripwire(
        kept, day="2026-10-05", stream=sys.stdout)
    print("    warnings:", fired, "| rows kept:", len(kept), "| merged:", merged)
    ok = fired == 1 and len(kept) == 2 and merged == 0
    print("  case:", "PASS" if ok else "FAIL")
    return ok


def main() -> int:
    pt = _load_picks_today()
    results = [_check_case(pt, *case) for case in CASES]
    results.append(_check_unjoinable(pt))
    ok = all(results)
    print("\nSMOKE:", "PASS" if ok else "FAIL",
          f"({sum(results)}/{len(results)} cases)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
