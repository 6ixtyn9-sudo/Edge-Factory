#!/usr/bin/env python3
"""Opt-in personal own-card match-page shadow capture; no production integration."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from edgefactory.sources import betexplorer_match_snapshot as source

LOCALDATA = Path(os.environ.get("EDGE_FACTORY_LOCALDATA") or ROOT / "localdata")


def capture(day: str, *, clock=None, sleep=time.sleep) -> list[dict]:
    """No URL discovery traffic: only explicit match URLs on today's own card."""
    clock = clock or (lambda: datetime.now(timezone.utc))
    if day != clock().astimezone(ZoneInfo("Africa/Johannesburg")).date().isoformat():
        raise ValueError("capture only today's card")
    if not 0 <= clock().astimezone(ZoneInfo("Africa/Johannesburg")).hour < 6:
        raise ValueError("off-peak window is 00:00–05:59 Africa/Johannesburg")
    # Retain only bounded shadow receipts; never touch other localdata families.
    for old in LOCALDATA.glob("betexplorer_match_shadow_????-??-??.json"):
        try:
            age = (clock().date() - datetime.strptime(old.stem[-10:], "%Y-%m-%d").date()).days
            if age > 30:
                old.unlink()
        except ValueError:
            continue
    path = LOCALDATA / "picks_today.json"
    raw = json.loads(path.read_text())
    rows = raw if isinstance(raw, list) else raw.get("picks", [])
    if not isinstance(rows, list):
        raise ValueError("invalid card")
    ledger = LOCALDATA / f"betexplorer_match_shadow_{day}.json"
    existing = json.loads(ledger.read_text()) if ledger.exists() else []
    if not isinstance(existing, list):
        raise ValueError("invalid ledger")
    seen = {(r["home_key"], r["away_key"]) for r in existing}
    last_request = None
    if existing:
        prior = datetime.fromisoformat(existing[-1]["attempted_at"])
        delay = (clock() - prior).total_seconds()
        if delay < 5.1:
            sleep(5.1 - max(0, delay))
    for row in rows:
        if not isinstance(row, dict) or str(row.get("date", ""))[:10] != day:
            continue
        hk, ak = source.source_team_key(row.get("home")), source.source_team_key(row.get("away"))
        if not hk or not ak or (hk, ak) in seen:
            continue
        url = row.get("betexplorer_match_url") or row.get("match_url")
        if not url:
            continue
        try:
            source.validated_url(url)
        except ValueError:
            continue
        seen.add((hk, ak))
        if last_request is not None:
            sleep(max(0, 5.1 - (time.monotonic() - last_request)))
        stamp = clock()
        # Reserve attempt BEFORE network: failure/crash cannot cause an automatic retry.
        item = {"date": day, "home_key": hk, "away_key": ak,
                "attempted_at": stamp.isoformat(), "status": "attempted",
                "page_sha256": None, "observed": None}
        existing.append(item)
        ledger.parent.mkdir(parents=True, exist_ok=True)
        ledger.write_text(json.dumps(existing, indent=2))
        last_request = time.monotonic()
        try:
            body, digest = source.fetch_page(url)
            item["page_sha256"] = digest
            # Identity cannot be inferred from URL slug alone. Unverified observations
            # are quarantined, not passed to ML or any card/odds lane.
            item["observed"] = source.parse_page(body)
            item["status"] = "unverified_identity"
        except Exception as exc:
            item["status"] = "failed_" + type(exc).__name__
            # Abort on any failure; never hammer a failing site.
            ledger.write_text(json.dumps(existing, indent=2))
            break
        ledger.write_text(json.dumps(existing, indent=2))
    return existing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", required=True)
    args = parser.parse_args()
    print(f"shadow ledger entries: {len(capture(args.date))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
