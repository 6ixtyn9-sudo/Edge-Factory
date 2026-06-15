#!/usr/bin/env python3
"""Sync certified edges + daily picks to Supabase.

CSV/DuckDB remains the live ingest path. This script only promotes the current
edge registry and the picks_today.json ledger into Supabase for dashboards / app
read models. It is failure-safe for fresh clones: missing localdata files simply
produce zero rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.db import get_client, upsert_edges, upsert_picks  # noqa: E402
from edgefactory.util import norm_team  # noqa: E402

EDGES = ROOT / "localdata" / "edges_consensus.json"
PICKS = ROOT / "localdata" / "picks_today.json"

SPORT_ID = 1          # sports.key='soccer'
SOURCE_ID = 1         # sources.key='forebet' / consensus base source
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
    """Load certified edges as rows for the Supabase edges table."""
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


def load_picks_raw() -> list[dict]:
    """Load picks_today.json. Missing/unreadable file -> zero rows."""
    try:
        data = json.loads(PICKS.read_text())
    except Exception:
        return []
    return data if isinstance(data, list) else []


def build_rule_aliases(edges: list[dict]) -> dict[str, str]:
    """Return alias -> exact edge name for old/new picks_today rule strings."""
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
    """Resolve a pick to an exact certified edge name."""
    for key in ("edge_rule", "rule", "display_rule"):
        val = pick.get(key)
        if val and val in aliases:
            return aliases[val]
    return pick.get("edge_rule") or pick.get("rule")


def event_source_ref(pick: dict) -> str:
    """Deterministic event natural key for the CSV/DuckDB promotion layer."""
    sport = pick.get("sport") or "soccer"
    day = pick.get("date") or date.today().isoformat()
    home = norm_team(pick.get("home") or "")
    away = norm_team(pick.get("away") or "")
    if not home or not away:
        # Last-resort stable fallback; avoid leaking massive payload into source_ref.
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
    """Upsert minimal event stubs and return source_ref -> event UUID."""
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
    return {r["source_ref"]: r["id"] for r in _response_data(resp)
            if r.get("source_ref") and r.get("id")}


def build_pick_rows(
    picks: list[dict],
    edge_ids: dict[str, str],
    event_ids: dict[str, str],
    aliases: dict[str, str],
) -> tuple[list[dict], list[dict]]:
    """Build Supabase edge_picks rows. Returns (rows, skipped)."""
    rows: list[dict] = []
    skipped: list[dict] = []
    for p in picks:
        edge_name = pick_edge_name(p, aliases)
        event_ref = event_source_ref(p)
        edge_id = edge_ids.get(edge_name or "")
        event_id = event_ids.get(event_ref)
        if not edge_id or not event_id:
            skipped.append({"pick": p, "edge_name": edge_name, "event_ref": event_ref})
            continue
        bucket = p.get("bucket") or "UNKNOWN"
        try:
            probability = round(float(p.get("avg_p")) / 100.0, 4)
        except Exception:
            probability = None
        rows.append({
            "edge_id": edge_id,
            "event_id": event_id,
            "market": p.get("market", "1x2"),
            "selection": p.get("pick"),
            "probability": probability,
            "odds": p.get("odds"),
            "status": "skipped" if str(bucket).startswith("SKIPPED") else "open",
            "bucket": bucket,
            "context": p.get("ctx", {}),
            "rule": edge_name,
            "match_name": p.get("match"),
            "picked_for": p.get("date"),
            "market_type": p.get("market_type") or p.get("market"),
            "odds_tier": p.get("odds_tier"),
            "source_payload": p,
        })
    return rows, skipped


def main() -> None:
    p = argparse.ArgumentParser(description="Sync certified edges and picks_today ledger to Supabase")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    edges = load_edges()
    raw_picks = load_picks_raw()
    aliases = build_rule_aliases(edges)
    print(f"Certified edges to sync: {len(edges)}")
    print(f"Daily picks to sync: {len(raw_picks)}")

    if args.dry_run:
        print("DRY RUN")
        return

    try:
        client = get_client()
        if edges:
            upsert_edges(client, edges)
        edge_ids = fetch_edge_ids(client, [e["name"] for e in edges])
        event_ids = upsert_events(client, raw_picks)
        pick_rows, skipped = build_pick_rows(raw_picks, edge_ids, event_ids, aliases)
        if skipped:
            print(f"Skipped picks without edge/event id: {len(skipped)}")
        if pick_rows:
            upsert_picks(client, pick_rows)
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
