#!/usr/bin/env python3
"""
Retrospective Results Backfill Helper (Phase 7.1)

Purpose:
Fill missing final scores (hs, gs, ht_hs, ht_gs) into source CSVs
using forebet as the source of truth.

This helps league_context and team_context mature faster
without changing any edge certification or purity rules.

Usage:
    PYTHONPATH=src python scripts/backfill_results.py 2026-06-01 2026-06-10

Safety rules:
- Only updates rows where hs/gs are currently NULL or empty.
- Never overwrites existing results.
- Only uses forebet_settled as the donor.
- Does NOT touch edges_consensus.json or purity_registry.json.
"""

from __future__ import annotations

import argparse
import glob
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"


def load_forebet_results() -> pd.DataFrame:
    """Load all settled forebet data as the source of truth."""
    files = sorted(glob.glob(str(LOCALDATA / "forebet_*.csv.gz")))
    if not files:
        print("No forebet files found. Run capture_daily first.")
        sys.exit(1)

    dfs = []
    for f in files:
        df = pd.read_csv(f, dtype=str)
        dfs.append(df)
    forebet = pd.concat(dfs, ignore_index=True)

    # Keep only settled matches
    forebet = forebet[forebet["hs"].notna() & forebet["gs"].notna()].copy()
    forebet["date"] = pd.to_datetime(forebet["date"]).dt.date.astype(str)

    # Normalize keys
    forebet["hkey"] = forebet["home"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
    forebet["akey"] = forebet["away"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)

    return forebet[["date", "hkey", "akey", "hs", "gs", "ht_hs", "ht_gs"]]


def backfill_source(source_name: str, forebet: pd.DataFrame, start: str, end: str):
    """Backfill missing results into one source's CSV files."""
    files = sorted(glob.glob(str(LOCALDATA / f"{source_name}_*.csv.gz")))
    if not files:
        print(f"No files for {source_name}")
        return 0

    updated_rows = 0

    for f in files:
        df = pd.read_csv(f, dtype=str)

        # Only process rows in the requested date range
        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        mask = (df["date"] >= start) & (df["date"] <= end)
        subset = df[mask].copy()

        if subset.empty:
            continue

        # Normalize keys for matching
        subset["hkey"] = subset["home"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        subset["akey"] = subset["away"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)

        # Find rows missing final scores
        missing = subset[
            subset["hs"].isna() | (subset["hs"] == "") |
            subset["gs"].isna() | (subset["gs"] == "")
        ].copy()

        if missing.empty:
            continue

        # Merge with forebet results
        merged = missing.merge(
            forebet,
            on=["date", "hkey", "akey"],
            how="left",
            suffixes=("", "_fb")
        )

        # Fill only where we have a match and the original was missing
        fill_mask = merged["hs_fb"].notna() & (
            merged["hs"].isna() | (merged["hs"] == "")
        )

        if fill_mask.any():
            merged.loc[fill_mask, "hs"] = merged.loc[fill_mask, "hs_fb"]
            merged.loc[fill_mask, "gs"] = merged.loc[fill_mask, "gs_fb"]
            merged.loc[fill_mask, "ht_hs"] = merged.loc[fill_mask, "ht_hs_fb"]
            merged.loc[fill_mask, "ht_gs"] = merged.loc[fill_mask, "ht_gs_fb"]

            updated_rows += fill_mask.sum()

            # Write back the changes
            df.loc[mask & (df.index.isin(missing.index)), ["hs", "gs", "ht_hs", "ht_gs"]] = \
                merged.loc[fill_mask, ["hs", "gs", "ht_hs", "ht_gs"]].values

            df.to_csv(f, index=False, compression="gzip")
            print(f"  {source_name}: updated {fill_mask.sum()} rows in {Path(f).name}")

    return updated_rows


def main():
    parser = argparse.ArgumentParser(description="Backfill missing final scores from forebet")
    parser.add_argument("start", help="Start date (YYYY-MM-DD)")
    parser.add_argument("end", help="End date (YYYY-MM-DD)")
    args = parser.parse_args()

    print(f"Retrospective results backfill: {args.start} → {args.end}")
    print("=" * 60)

    forebet = load_forebet_results()
    print(f"Loaded {len(forebet)} settled forebet matches as source of truth.\n")

    total_updated = 0
    for source in ["zulubet", "statarea", "vitibet", "scoutingstats", "betclan"]:
        updated = backfill_source(source, forebet, args.start, args.end)
        total_updated += updated

    print(f"\nTotal rows updated across all sources: {total_updated}")
    print("Re-run build_warehouse.py + assay_purity.py to refresh contexts.")


if __name__ == "__main__":
    main()
