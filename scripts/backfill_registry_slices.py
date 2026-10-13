#!/usr/bin/env python3
"""Backfill the floor-slice fields on registry records (round 6, R2, §3).

The registry's settled records carry ``league`` and the fixture's team names/keys
only from the moment ``record_outcome`` started accepting them. Everything
recorded before that has none — so the league level of the floor hierarchy is
inert until those records are attributed. This tool attributes them **from the
committed picks**, never from a guess:

* for each record, read the day's picks out of git
  (``git show <ref>:localdata/picks_<date>.json`` — the committed data, never the
  working tree) and find the pick whose fixture is the record's match;
* take that pick's ``league`` and its ``home``/``away`` names, and derive the
  identity keys with the repo's own ``source_team_key``;
* leave the record untouched when the day's picks do not contain it. Unmatched
  records stay ``league: null`` and simply **inherit** their parent floor — a
  guess about which league a match belonged to is exactly the kind of invented
  evidence this registry exists to prevent.

The dedup key is unchanged, no other field is touched, and re-running is a no-op
(records that already carry the fields are skipped). Coverage is printed for
every run: matched / total, league %, keys %, and the unmatched records.

Usage::

    python scripts/backfill_registry_slices.py --dry-run     # measure, write nothing
    python scripts/backfill_registry_slices.py --apply       # atomically rewrite the registry
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.enh_registry import (  # noqa: E402
    REGISTRY_VERSION, _locked, _read, _write_atomic, registry_path,
)


def _picks_for_day(ref: str, day: str) -> list[dict]:
    """The committed pick list for one day, or [] when there is none."""
    path = f"localdata/picks_{str(day)[:10]}.json"
    proc = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return []
    try:
        payload = json.loads(proc.stdout)
    except ValueError:
        return []
    picks = payload.get("picks") if isinstance(payload, dict) else payload
    return [p for p in picks if isinstance(p, dict)] if isinstance(picks, list) else []


def _find_pick(record: dict, picks: list[dict]) -> dict | None:
    """The pick whose fixture is this record's match, or None."""
    match = str(record.get("match") or "").strip()
    if not match:
        return None
    for pick in picks:
        if str(pick.get("match") or "").strip() == match:
            return pick
    # A record's match is "Home vs Away"; fall back to the pair when the
    # stored `match` string differs (archived spellings, dash separators).
    for pick in picks:
        home, away = str(pick.get("home") or "").strip(), str(pick.get("away") or "").strip()
        if home and away and f"{home} vs {away}" == match:
            return pick
    return None


def backfill(root: Path, *, ref: str, apply: bool) -> dict:
    path = registry_path(root)
    with _locked(root):
        reg = _read(path)
        markets = reg.get("markets") if isinstance(reg, dict) else None
        markets = markets if isinstance(markets, dict) else {}

        days: dict[str, list[dict]] = {}
        total = matched = already = 0
        with_league = with_keys = 0
        unmatched: list[str] = []

        for market, entry in sorted(markets.items()):
            for rec in (entry or {}).get("records") or []:
                if not isinstance(rec, dict):
                    continue
                total += 1
                if str(rec.get("league") or "").strip() and str(rec.get("home_key") or "").strip():
                    already += 1
                    with_league += 1
                    with_keys += 1
                    continue
                day = str(rec.get("date") or "")[:10]
                if day not in days:
                    days[day] = _picks_for_day(ref, day)
                pick = _find_pick(rec, days[day])
                if pick is None:
                    unmatched.append(f"{day} {rec.get('match')}")
                    continue
                matched += 1
                league = str(pick.get("league") or "").strip()
                home = str(pick.get("home") or "").strip()
                away = str(pick.get("away") or "").strip()
                rec.setdefault("league", league)
                rec.setdefault("home", home)
                rec.setdefault("away", away)
                if not str(rec.get("home_key") or "").strip() and home:
                    try:
                        from edgefactory.identity import source_team_key
                        rec["home_key"] = source_team_key(home)
                        rec["away_key"] = source_team_key(away)
                    except Exception:
                        pass
                if league:
                    with_league += 1
                if str(rec.get("home_key") or "").strip():
                    with_keys += 1

        coverage = {
            "records": total,
            "matched": matched,
            "already_attributed": already,
            "unmatched": len(unmatched),
            "with_league": with_league,
            "with_keys": with_keys,
            "league_pct": round(100.0 * with_league / total, 1) if total else 0.0,
            "keys_pct": round(100.0 * with_keys / total, 1) if total else 0.0,
            "unmatched_sample": unmatched[:10],
        }
        if apply and (matched or already == total):
            reg.setdefault("version", 2)
            _write_atomic(path, reg)
    return coverage


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--ref", default="origin/main",
                    help="git ref carrying the committed picks (default: origin/main)")
    group = ap.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="write the registry")
    group.add_argument("--dry-run", action="store_true", help="measure only (default)")
    args = ap.parse_args()

    coverage = backfill(Path(args.root), ref=args.ref, apply=bool(args.apply))
    print(f"backfill_registry_slices: ref={args.ref} "
          f"mode={'apply' if args.apply else 'dry-run'}")
    print(json.dumps(coverage, indent=2, sort_keys=True))
    if coverage["unmatched"]:
        print("unmatched records keep league: null and inherit their parent floor")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
