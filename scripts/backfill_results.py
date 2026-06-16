#!/usr/bin/env python3
"""
Retrospective Results Backfill Helper.

Backfills missing final scores into sources that store hs/gs, using settled donor
sources already captured in localdata/*.csv.gz.

Default mode is D30 so nightly.py can safely run it after capture_daily and
before build_warehouse:

    python3 scripts/backfill_results.py --days 30

Explicit date windows are still supported:

    python3 scripts/backfill_results.py 2026-06-01 2026-06-16
    python3 scripts/backfill_results.py --start 2026-06-01 --end 2026-06-16
"""

from __future__ import annotations

import argparse
import glob
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

# Sources that can have final scores.
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


def _norm_key(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.lower().str.replace(r"[^a-z0-9]", "", regex=True)


def load_donor_results() -> pd.DataFrame:
    all_results: list[pd.DataFrame] = []

    for source in DONOR_SOURCES:
        base = source.split("_")[0]
        files = sorted(glob.glob(str(LOCALDATA / f"{base}_*.csv.gz")))
        if not files:
            continue

        dfs: list[pd.DataFrame] = []
        for f in files:
            try:
                dfs.append(pd.read_csv(f, dtype=str))
            except Exception as exc:  # noqa: BLE001 - one bad cache file should not kill all donors
                print(f"  WARN: could not read donor file {Path(f).name}: {exc}")

        if not dfs:
            continue

        df = pd.concat(dfs, ignore_index=True)
        required = {"date", "home", "away", "hs", "gs"}
        if not required.issubset(df.columns):
            continue

        df = df[df["hs"].notna() & df["gs"].notna()].copy()
        df = df[(df["hs"].astype(str) != "") & (df["gs"].astype(str) != "")].copy()
        if df.empty:
            continue

        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)
        df = df[df["date"].notna() & (df["date"] != "NaT")].copy()
        df["hkey"] = _norm_key(df["home"])
        df["akey"] = _norm_key(df["away"])

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


def backfill_source(source_name: str, donor_df: pd.DataFrame, start: str, end: str) -> int:
    files = sorted(glob.glob(str(LOCALDATA / f"{source_name}_*.csv.gz")))
    if not files:
        return 0

    updated_rows = 0
    donor_has_ht_cols = "ht_hs" in donor_df.columns and "ht_gs" in donor_df.columns

    for f in files:
        df = pd.read_csv(f, dtype=str)
        required = {"date", "home", "away", "hs", "gs"}
        if not required.issubset(df.columns):
            continue

        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date.astype(str)
        mask = (df["date"] >= start) & (df["date"] <= end)
        subset = df.loc[mask].copy()
        if subset.empty:
            continue

        subset["hkey"] = _norm_key(subset["home"])
        subset["akey"] = _norm_key(subset["away"])
        missing = subset[
            subset["hs"].isna()
            | (subset["hs"].astype(str) == "")
            | subset["gs"].isna()
            | (subset["gs"].astype(str) == "")
        ].copy()
        if missing.empty:
            continue

        merged = missing.merge(
            donor_df,
            on=["date", "hkey", "akey"],
            how="left",
            suffixes=("", "_donor"),
        )

        fill_mask = merged["hs_donor"].notna() & (
            merged["hs"].isna() | (merged["hs"].astype(str) == "")
        )
        if not fill_mask.any():
            continue

        merged.loc[fill_mask, "hs"] = merged.loc[fill_mask, "hs_donor"]
        merged.loc[fill_mask, "gs"] = merged.loc[fill_mask, "gs_donor"]

        update_cols = ["hs", "gs"]
        if donor_has_ht_cols and "ht_hs" in merged.columns and "ht_hs_donor" in merged.columns:
            ht_mask = fill_mask & merged["ht_hs_donor"].notna()
            if ht_mask.any():
                merged.loc[ht_mask, "ht_hs"] = merged.loc[ht_mask, "ht_hs_donor"]
                merged.loc[ht_mask, "ht_gs"] = merged.loc[ht_mask, "ht_gs_donor"]
            if "ht_hs" in df.columns and "ht_gs" in df.columns:
                update_cols += ["ht_hs", "ht_gs"]

        # merged keeps the original df index from missing as its index only if merge
        # preserves it as a column; capture explicitly before merge via reset_index.
        # For the common path above, missing's index is not reliable after merge.
        missing_with_index = missing.reset_index(names="_row_index")
        merged_with_index = missing_with_index.merge(
            donor_df,
            on=["date", "hkey", "akey"],
            how="left",
            suffixes=("", "_donor"),
        )
        fill_mask2 = merged_with_index["hs_donor"].notna() & (
            merged_with_index["hs"].isna() | (merged_with_index["hs"].astype(str) == "")
        )
        if not fill_mask2.any():
            continue

        merged_with_index.loc[fill_mask2, "hs"] = merged_with_index.loc[fill_mask2, "hs_donor"]
        merged_with_index.loc[fill_mask2, "gs"] = merged_with_index.loc[fill_mask2, "gs_donor"]
        if donor_has_ht_cols and "ht_hs" in merged_with_index.columns and "ht_hs_donor" in merged_with_index.columns:
            ht_mask2 = fill_mask2 & merged_with_index["ht_hs_donor"].notna()
            if ht_mask2.any():
                merged_with_index.loc[ht_mask2, "ht_hs"] = merged_with_index.loc[ht_mask2, "ht_hs_donor"]
                merged_with_index.loc[ht_mask2, "ht_gs"] = merged_with_index.loc[ht_mask2, "ht_gs_donor"]

        rows = merged_with_index.loc[fill_mask2, "_row_index"]
        df.loc[rows, update_cols] = merged_with_index.loc[fill_mask2, update_cols].values
        df.to_csv(f, index=False, compression="gzip")

        count = int(fill_mask2.sum())
        updated_rows += count
        print(f"  {source_name}: updated {count} rows in {Path(f).name}")

    return updated_rows


def resolve_window(args: argparse.Namespace) -> tuple[str, str]:
    if args.pos_start and args.start and args.pos_start != args.start:
        raise SystemExit("Provide start either positionally or via --start, not both.")
    if args.pos_end and args.end and args.pos_end != args.end:
        raise SystemExit("Provide end either positionally or via --end, not both.")

    today = date.today()
    end = args.end or args.pos_end or today.isoformat()
    start = args.start or args.pos_start or (today - timedelta(days=args.days)).isoformat()
    return start, end


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Retrospective results backfill — fills missing hs/gs from donor sources."
    )
    parser.add_argument("pos_start", nargs="?", help="Start date YYYY-MM-DD")
    parser.add_argument("pos_end", nargs="?", help="End date YYYY-MM-DD")
    parser.add_argument("--start", help="Start date YYYY-MM-DD")
    parser.add_argument("--end", help="End date YYYY-MM-DD")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Backfill window in days if start/end not given (default: 30)",
    )
    args = parser.parse_args()

    start, end = resolve_window(args)

    print(f"Multi-source retrospective results backfill: {start} → {end}")
    print("=" * 65)

    donor_df = load_donor_results()
    print(f"Loaded {len(donor_df)} unique settled matches from all donors.\n")

    total = 0
    for source in TARGET_SOURCES_WITH_RESULTS:
        total += backfill_source(source, donor_df, start, end)

    print(f"\nTotal rows updated: {total}")
    print("Run: python3 scripts/build_warehouse.py && PYTHONPATH=src python3 scripts/assay_purity.py")


if __name__ == "__main__":
    main()
