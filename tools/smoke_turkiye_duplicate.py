#!/usr/bin/env python3
"""CLI smoke for the Türkiye/Turkey duplicate-fixture split (2026-10-05).

Runs entirely on controlled in-memory fixture data (no network, no
localdata writes) and prints:

  * the key derivation for both spellings (alias application is visible);
  * the operational collapse result: ONE surviving pick, one
    ``duplicate_fixture`` rejection for the twin;
  * the near-duplicate tripwire staying silent (the curated alias already
    joined the pair) and firing on a genuinely unjoined pair;
  * settlement grading a pick captured as "Türkiye" from a result
    recorded as "Turkey".

Usage:  python tools/smoke_turkiye_duplicate.py
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


def main() -> int:
    pt = _load_picks_today()

    print("== key derivation ==")
    for name in ("Türkiye", "Turkey"):
        print(" ", json.dumps(explain_team_key(name), ensure_ascii=False))

    rows = [
        _pick("Italy", "Türkiye", 1.42, "05-10, 19:45", 0.70, "zulubet", 900),
        _pick("Italy", "Turkey", 1.47, "14:45", 0.64, "betexplorer", 1810),
    ]

    print("\n== canonical fixture identity ==")
    for r in rows:
        print(" ", r["match"], "->", pt.canonical_fixture_identity(r))

    collapsed, removed = pt.collapse_final_operational_picks(rows)
    print("\n== operational collapse ==")
    print("  surviving picks:", len(collapsed), "| collapsed twins:", removed)
    for r in collapsed:
        print("   kept:", r["match"], "@", r["odds"], "| ctx:",
              r.get("ctx", {}).get("duplicate_alias_collapse"))
    print("  twin rejection code persisted by the shadow ledger:",
          "duplicate_fixture" if removed else "NONE")

    print("\n== shadow identity ==")
    print("  fixture_id equal:",
          fixture_id(rows[0], "2026-10-05") == fixture_id(rows[1], "2026-10-05"))
    print("  candidate_id equal:",
          candidate_id(rows[0], "2026-10-05") == candidate_id(rows[1], "2026-10-05"))

    print("\n== tripwire (alias resolved the pair -> must be silent) ==")
    fired = pt.print_near_duplicate_fixture_tripwire(collapsed, day="2026-10-05",
                                                     stream=sys.stdout)
    print("  warnings:", fired)

    print("\n== tripwire (no alias available -> must fire, merge nothing) ==")
    unjoined = [
        _pick("Italy", "Greece", 1.42, "05-10, 19:45", 0.70, "zulubet", 900),
        _pick("Italy", "Portugal", 1.47, "05-10, 19:45", 0.64, "betexplorer", 900),
    ]
    kept, dropped = pt.collapse_final_operational_picks(unjoined)
    fired2 = pt.print_near_duplicate_fixture_tripwire(kept, day="2026-10-05",
                                                      stream=sys.stdout)
    print("  warnings:", fired2, "| rows kept:", len(kept), "| merged:", dropped)

    print("\n== settlement across spellings ==")
    settled = {("2026-10-05", canonical_team_key("Italy"),
                canonical_team_key("Turkey")): "home"}
    out = settle_candidate({"market": "1x2", "selection_side": "home",
                            "home_team": "Italy", "away_team": "Türkiye",
                            "trading_date": "2026-10-05"}, settled)
    print("  result recorded as 'Turkey' grades pick captured as 'Türkiye':", out)

    ok = (len(collapsed) == 1 and removed == 1 and fired == 0
          and fired2 == 1 and dropped == 0
          and out["settlement_status"] == "win")
    print("\nSMOKE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
