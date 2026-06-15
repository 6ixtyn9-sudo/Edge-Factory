#!/usr/bin/env python3
"""
Retrospective Results Backfill Helper (Phase 7.1) - Final Version

Only backfills into sources that store final scores.
Skips pure prediction sources (betclan, bzzoiro, etc.).
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

# Sources that can have final scores (from warehouse.py)
TARGET_SOURCES_WITH_RESULTS = [
    "zulubet",
    "statarea",
    "vitibet",
    "scoutingstats",
    "bettingclosed",
]

DONOR_SOURCES = [
    "forebet_settled",
    "statarea_settled",
    "zulubet_settled",
    "bettingclosed_settled",
]


def load_donor_results() -> pd.DataFrame:
    all_results = []

    for source in DONOR_SOURCES:
        base = source.split("_")[0]
        files = sorted(glob.glob(str(LOCALDATA / f"{base}_*.csv.gz")))
        if not files:
            continue

        dfs = []
        for f in files:
            try:
                df = pd.read_csv(f, dtype=str)
                dfs.append(df)
            except Exception:
                continue

        if not dfs:
            continue

        df = pd.concat(dfs, ignore_index=True)
        df = df[df["hs"].notna() & df["gs"].notna()].copy()

        if df.empty:
            continue

        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)
        df["hkey"] = df["home"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        df["akey"] = df["away"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)

        cols = ["date", "hkey", "akey", "hs", "gs"]
        if "ht_hs" in df.columns and "ht_gs" in df.columns:
            cols += ["ht_hs", "ht_gs"]

        all_results.append(df[cols])

    if not all_results:
        print("No donor data found.")
        sys.exit(1)

    combined = pd.concat(all_results, ignore_index=True)
    combined = combined.drop_duplicates(subset=["date", "hkey", "akey"], keep="first")
    return combined


def backfill_source(source_name: str, donor_df: pd.DataFrame, start: str, end: str):
    files = sorted(glob.glob(str(LOCALDATA / f"{source_name}_*.csv.gz")))
    if not files:
        return 0

    updated_rows = 0
    has_ht_cols = "ht_hs" in donor_df.columns and "ht_gs" in donor_df.columns

    for f in files:
        df = pd.read_csv(f, dtype=str)

        # Skip sources that don't have hs/gs columns
        if "hs" not in df.columns or "gs" not in df.columns:
            continue

        df["date"] = pd.to_datetime(df["date"]).dt.date.astype(str)

        mask = (df["date"] >= start) & (df["date"] <= end)
        subset = df.loc[mask].copy()
        if subset.empty:
            continue

        subset["hkey"] = subset["home"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)
        subset["akey"] = subset["away"].str.lower().str.replace(r"[^a-z0-9]", "", regex=True)

        missing = subset[
            subset["hs"].isna() | (subset["hs"] == "") |
            subset["gs"].isna() | (subset["gs"] == "")
        ].copy()

        if missing.empty:
            continue

        merged = missing.merge(
            donor_df,
            on=["date", "hkey", "akey"],
            how="left",
            suffixes=("", "_donor")
        )

        fill_mask = merged["hs_donor"].notna() & (
            merged["hs"].isna() | (merged["hs"] == "")
        )

        if fill_mask.any():
            merged.loc[fill_mask, "hs"] = merged.loc[fill_mask, "hs_donor"]
            merged.loc[fill_mask, "gs"] = merged.loc[fill_mask, "gs_donor"]

            if has_ht_cols and "ht_hs_donor" in merged.columns and "ht_gs_donor" in merged.columns:
                ht_mask = fill_mask & merged["ht_hs_donor"].notna()
                if ht_mask.any():
                    merged.loc[ht_mask, "ht_hs"] = merged.loc[ht_mask, "ht_hs_donor"]
                    merged.loc[ht_mask, "ht_gs"] = merged.loc[ht_mask, "ht_gs_donor"]

            update_cols = ["hs", "gs"]
            if has_ht_cols and "ht_hs" in merged.columns:
                update_cols += ["ht_hs", "ht_gs"]

            df.loc[merged.loc[fill_mask].index, update_cols] = merged.loc[fill_mask, update_cols].values
            updated_rows += fill_mask.sum()
            print(f"  {source_name}: updated {fill_mask.sum()} rows in {Path(f).name}")

    return updated_rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("start")
    parser.add_argument("end")
    args = parser.parse_args()

    print(f"Multi-source retrospective results backfill: {args.start} → {args.end}")
    print("=" * 65)

    donor_df = load_donor_results()
    print(f"Loaded {len(donor_df)} unique settled matches from all donors.\n")

    total = 0
    for source in TARGET_SOURCES_WITH_RESULTS:
        total += backfill_source(source, donor_df, args.start, args.end)

    print(f"\nTotal rows updated: {total}")
    print("Run: python scripts/build_warehouse.py && PYTHONPATH=src python scripts/assay_purity.py")


if __name__ == "__main__":
    main()