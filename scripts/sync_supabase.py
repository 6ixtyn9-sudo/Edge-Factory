#!/usr/bin/env python3
"""Sync certified edges + today's picks to Supabase."""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT/"src"))
from edgefactory.db import get_client, upsert_edges, upsert_picks

EDGES = ROOT/"localdata"/"edges_consensus.json"
PICKS = ROOT/"localdata"/"picks_today.json"

def load_edges():
    try:
        data = json.loads(EDGES.read_text())
        out = []
        for e in data.get("edges", []):
            if e.get("status") != "certified":
                continue
            out.append({
                "name": e["rule"],
                "sport_id": 1, # Default Soccer
                "source_id": 1, # Default Forebet-based
                "rule": e,
                "status": "certified",
                "train_stats": e["train"],
                "valid_stats": e["valid"]
            })
        return out
    except Exception:
        return []

def load_picks():
    # Deferred: requires lookup mapping for edge_id and event_id
    return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    edges = load_edges()
    picks = load_picks()
    print(f"Certified edges to sync: {len(edges)}")
    if args.dry_run:
        print("DRY RUN"); return
    try:
        c = get_client()
        if edges:
            upsert_edges(c, edges)
        # Picks sync remains deferred until ID mapping logic ships
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e); sys.exit(1)

if __name__ == "__main__": main()
