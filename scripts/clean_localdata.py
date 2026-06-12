#!/usr/bin/env python3
"""Clean stale files from localdata/ (run manually when needed)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

KEEP_PATTERNS = [
    "edges_consensus.json",
    "picks_*.txt",
    "picks_today.json",
    "warehouse.duckdb",
    "state_*.json",
    "*.csv.gz",
    ".gitkeep",
    "README.md",
]

def main():
    print("Cleaning localdata/ ...")
    for f in LOCALDATA.iterdir():
        if f.is_file():
            keep = any(f.match(p) for p in KEEP_PATTERNS)
            if not keep:
                print(f"  Removing stale: {f.name}")
                f.unlink()
    print("Done.")

if __name__ == "__main__":
    main()
