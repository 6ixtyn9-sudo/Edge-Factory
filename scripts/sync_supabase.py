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
        return [e for e in data.get("edges", []) if e.get("status")=="certified"]
    except: return []

def load_picks():
    try:
        if PICKS.exists():
            return json.loads(PICKS.read_text())
    except: pass
    return []

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    edges = load_edges()
    picks = load_picks()
    print(f"Certified edges: {len(edges)}")
    print(f"Today's picks: {len(picks)}")
    if args.dry_run:
        print("DRY RUN"); return
    try:
        c = get_client()
        upsert_edges(c, edges)
        if picks: upsert_picks(c, picks)
        print("Supabase sync done.")
    except Exception as e:
        print("Sync failed:", e); sys.exit(1)

if __name__ == "__main__": main()
