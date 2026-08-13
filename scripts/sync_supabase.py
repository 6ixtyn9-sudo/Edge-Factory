#!/usr/bin/env python3
"""Sync certified edges + daily picks to Supabase.

CSV/DuckDB remains the live ingest path. This script promotes the current edge
registry and an explicit picks ledger into Supabase for dashboards / app read
models. It supports authoritative replace-for-date syncing so stale same-day
rows cannot survive downstream.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.db import delete_picks_for_date, get_client, upsert_edges, upsert_picks  # noqa: E402
from edgefactory.util import ledger_team_key  # noqa: E402

EDGES = ROOT / "localdata" / "edges_consensus.json"
DEFAULT_PICKS = ROOT / "localdata" / "picks_today.json"

SPORT_ID = 1  # sports.key='soccer'
SOURCE_ID = 1  # sources.key='forebet' / consensus base source
EVENT_SOURCE_KEY = "edgefactory_picks"


def _response_data(resp) -> list[dict]:
    return list(getattr(resp, "data", None) or [])


def _display_rule_from_name(name: str, market: str = "1x2") -> str | None:
    """Map miner rule names to the short picks_today display label."""
    import re

    mn = re.search(r"(\d+)\s*way", name or "", re.I)
    mt = re.search(r"avg_p\s*>=?\s*([\d.]+)", name or "", re.I)
    if not mn or not mt:
        return None
    n_way = int(mn.group(1))
    thr = float(mt.group(1))
    if market == "ou_2.5":
        return f"OU25-UNANIMOUS-{n_way}WAY≥{thr:.0f}"
    if market == "btts":
        return f"BTTS-UNANIMOUS-{n_way}WAY≥{thr:.0f}"
    return f"{n_way}WAY-UNANIMOUS≥{thr:.0f}"


def load_edges() -> list[dict]:
    try:
        data = json.loads(EDGES.read_text())
    except Exception:
        return []

    out = []
    for e in data.get("edges", []):
        if e.get("status") != "certified":
            continue
        decay = e.get("decay", {}) if isinstance(e.get("decay"), dict) else {}
        out.append({
            "name": e["rule"],
            "sport_id": SPORT_ID,
            "source_id": SOURCE_ID,
            "rule": e,
            "status": "certified",
            "train_stats": e.get("train", {}),
            "valid_stats": e.get("valid", {}),
            "decay_verdict": decay.get("verdict", "unknown"),
        })
    return out


def load_picks_raw(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def infer_target_date(picks: list[dict], fallback: str | None = None) -> str | None:
    if fallback:
        return fallback
    for p in picks:
        value = str(p.get("picked_for") or p.get("date") or "")[:10]
        if value:
            return value
    return None


def build_rule_aliases(edges: list[dict]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for e in edges:
        name = e.get("name")
        if not name:
            continue
        aliases[name] = name
        rule = e.get("rule", {}) if isinstance(e.get("rule"), dict) else {}
        display = _display_rule_from_name(name, rule.get("market", "1x2"))
        if display:
            aliases[display] = name
    return aliases


def pick_edge_name(pick: dict, aliases: dict[str, str]) -> str | None:
    for key in ("edge_rule", "rule", "display_rule"):
        val = pick.get(key)
        if val and val in aliases:
            return aliases[val]
    return pick.get("edge_rule") or pick.get("rule")


def event_source_ref(pick: dict) -> str:
    sport = pick.get("sport") or "soccer"
    day = pick.get("date") or date.today().isoformat()
    home = ledger_team_key(pick.get("home") or "")
    away = ledger_team_key(pick.get("away") or "")
    if not home or not away:
        digest = hashlib.sha1(json.dumps(pick, sort_keys=True).encode()).hexdigest()[:16]
        home, away = "unknown", digest
    return f"{sport}|{day}|{home}|{away}"


def event_row_from_pick(pick: dict) -> dict:
    day = pick.get("date") or date.today().isoformat()
    return {
        "sport_id": SPORT_ID,
        "start_time": f"{day}T12:00:00+00:00",
        "source_key": EVENT_SOURCE_KEY,
        "source_ref": event_source_ref(pick),
        "status": "scheduled",
    }


def fetch_edge_ids(client, edge_names: list[str]) -> dict[str, str]:
    if not edge_names:
        return {}
    resp = (
        client.table("edges")
        .select("id,name")
        .eq("sport_id", SPORT_ID)
        .eq("source_id", SOURCE_ID)
        .in_("name", sorted(set(edge_names)))
        .execute()
    )
    return {r["name"]: r["id"] for r in _response_data(resp) if r.get("name") and r.get("id")}


def upsert_events(client, picks: list[dict]) -> dict[str, str]:
    if not picks:
        return {}
    by_ref = {event_source_ref(p): event_row_from_pick(p) for p in picks}
    rows = list(by_ref.values())
    client.table("events").upsert(rows, on_conflict="source_key,source_ref").execute()
    resp = (
        client.table("events")
        .select("id,source_ref")
        .eq("source_key", EVENT_SOURCE_KEY)
        .in_("source_ref", sorted(by_ref))
        .execute()
    )
    return {
        r["source_ref"]: r["id"]
        for r in _response_data(resp)
        if r.get("source_ref") and r.get("id")
    }


def _sync_meta(target_date: str, picks_path: Path) -> dict[str, Any]:
    return {
        "producer": "edgefactory",
        "target_date": target_date,
        "sync_mode": "authoritative_replace",
        "synced_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_file": str(picks_path),
    }


def build_pick_rows(
    picks: list[dict],
    edge_ids: dict[str, str],
    event_ids: dict[str, str],
    aliases: dict[str, str],
    *,
    target_date: str,
    picks_path: Path,
) -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    skipped: list[dict] = []
    seen_conflicts: set[tuple[Any, Any, Any, Any]] = set()
    sync_meta = _sync_meta(target_date, picks_path)
    for p in picks:
        edge_name = pick_edge_name(p, aliases)
        event_ref = event_source_ref(p)
        edge_id = edge_ids.get(edge_name or "")
        event_id = event_ids.get(event_ref)
        if not edge_id or not event_id:
            skipped.append({
                "pick": p,
                "edge_name": edge_name,
                "event_ref": event_ref,
                "reason": "missing_edge_or_event_id",
            })
            continue
        bucket = p.get("bucket") or "UNKNOWN"
        try:
            probability = round(float(p.get("avg_p")) / 100.0, 4)
        except Exception:
            probability = None
        market = p.get("market", "1x2")
        selection = p.get("pick")
        conflict_key = (edge_id, event_id, market, selection)
        if conflict_key in seen_conflicts:
            # Postgres rejects an UPSERT batch that proposes the same unique
            # key twice (SQLSTATE 21000). Keep the first frozen payload and
            # quarantine the duplicate instead of deleting the date then
            # failing to repopulate it.
            skipped.append({
                "pick": p,
                "edge_name": edge_name,
                "event_ref": event_ref,
                "reason": "duplicate_conflict_key",
            })
            continue
        seen_conflicts.add(conflict_key)

        payload = dict(p)
        payload["_sync_meta"] = sync_meta
        rows.append({
            "edge_id": edge_id,
            "event_id": event_id,
            "market": market,
            "selection": selection,
            "probability": probability,
            "odds": p.get("odds"),
            "status": "skipped" if str(bucket).startswith("SKIPPED") else "open",
            "bucket": bucket,
            "context": {**(p.get("ctx", {}) or {}), "_sync_meta": sync_meta},
            "rule": edge_name,
            "match_name": p.get("match"),
            "picked_for": (p.get("date") or target_date)[:10],
            "market_type": p.get("market_type") or p.get("market"),
            "odds_tier": p.get("odds_tier"),
            "source_payload": payload,
        })
    return rows, skipped


def write_sync_manifest(*, target_date: str, picks_path: Path, raw_text: str, pick_rows: list[dict], replace_date: bool) -> Path:
    manifest = {
        "target_date": target_date,
        "picks_path": str(picks_path),
        "row_count": len(pick_rows),
        "sha1": hashlib.sha1(raw_text.encode()).hexdigest(),
        "sync_mode": "authoritative_replace" if replace_date else "upsert_only",
        "written_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    out = ROOT / "localdata" / f"supabase_sync_manifest_{target_date}.json"
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True))
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Sync certified edges and an explicit picks ledger to Supabase")
    p.add_argument("--picks", default=str(DEFAULT_PICKS), help="Path to source picks JSON.")
    p.add_argument("--target-date", default=None, help="Authoritative target date (YYYY-MM-DD).")
    p.add_argument("--replace-date", action="store_true", help="Delete existing rows for target date before upserting.")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    picks_path = Path(args.picks)
    raw_text = picks_path.read_text() if picks_path.exists() else "[]"
    edges = load_edges()
    raw_picks = load_picks_raw(picks_path)
    target_date = infer_target_date(raw_picks, args.target_date)
    aliases = build_rule_aliases(edges)

    print(f"Certified edges to sync: {len(edges)}")
    print(f"Daily picks to sync: {len(raw_picks)}")
    print(f"Sync source file: {picks_path}")
    print(f"Target date: {target_date}")
    print(f"Replace date mode: {args.replace_date}")

    if args.dry_run:
        print("DRY RUN")
        return

    if args.replace_date and not target_date:
        print("Sync failed: --replace-date requires --target-date or picks with a date field")
        sys.exit(1)

    try:
        client = get_client()
        if edges:
            upsert_edges(client, edges)
        edge_ids = fetch_edge_ids(client, [e["name"] for e in edges])
        event_ids = upsert_events(client, raw_picks)
        pick_rows, skipped = build_pick_rows(
            raw_picks,
            edge_ids,
            event_ids,
            aliases,
            target_date=target_date or date.today().isoformat(),
            picks_path=picks_path,
        )
        if skipped:
            reasons: dict[str, int] = {}
            for item in skipped:
                reason = str(item.get("reason") or "missing_edge_or_event_id")
                reasons[reason] = reasons.get(reason, 0) + 1
            detail = ", ".join(f"{reason}={count}" for reason, count in sorted(reasons.items()))
            print(f"Skipped picks: {len(skipped)} ({detail})")

        # Prepare and validate the complete replacement batch before deleting
        # the currently published date. The old order deleted first, so a
        # duplicate-batch SQLSTATE 21000 left the date empty.
        if args.replace_date and raw_picks and not pick_rows:
            raise RuntimeError(
                "refusing to delete existing date: non-empty source produced zero syncable picks"
            )
        if args.replace_date and target_date:
            delete_picks_for_date(client, target_date)
        if pick_rows:
            upsert_picks(client, pick_rows)
        manifest = write_sync_manifest(
            target_date=target_date or date.today().isoformat(),
            picks_path=picks_path,
            raw_text=raw_text,
            pick_rows=pick_rows,
            replace_date=args.replace_date,
        )
        print(f"Sync manifest written: {manifest}")
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
