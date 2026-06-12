#!/usr/bin/env python3
"""Sync certified edges and daily picks to Supabase.

Usage:
    python3 scripts/sync_supabase.py --dry-run
    python3 scripts/sync_supabase.py
"""

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.db import get_client, upsert_edges, upsert_picks
from edgefactory.config import GATES


EDGES_PATH = ROOT / "localdata" / "edges_consensus.json"


def load_certified_edges():
    """Load only certified edges from the consensus registry."""
    try:
        data = json.loads(EDGES_PATH.read_text())
        return [e for e in data.get("edges", []) if e.get("status") == "certified"]
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    edges = load_certified_edges()
    print(f"Found {len(edges)} certified edges in registry")

    if args.dry_run:
        print("DRY RUN — nothing pushed to Supabase")
        return

    try:
        client = get_client()
        upsert_edges(client, edges)
        print("Sync complete.")
    except Exception as e:
        print(f"Sync failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
