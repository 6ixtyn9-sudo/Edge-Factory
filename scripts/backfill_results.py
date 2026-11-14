#!/usr/bin/env python3
"""Retrospective results backfill helper.

Fills missing final scores (hs/gs) in score-capable source cache files using
settled donor sources already captured in localdata/*.csv.gz.

Default mode is D30 so daily.py can run it after capture_daily and before
build_warehouse:

    python3 scripts/backfill_results.py --days 30

Explicit date windows are still supported:

    python3 scripts/backfill_results.py 2026-06-01 2026-06-16
    python3 scripts/backfill_results.py --start 2026-06-01 --end 2026-06-16

This script is intentionally idempotent: it only writes rows where hs/gs are
missing and a donor result exists.
"""

from __future__ import annotations

import argparse
import glob
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import NamedTuple

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"

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


class BackfillResult(NamedTuple):
    updated_rows: int
    updated_files: int
    file_counts: dict[str, int]


def _norm_key(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.lower().str.replace(r"[^a-z0-9]", "", regex=True)


def _normalise_date(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.date.astype(str)


def load_donor_results(start: str, end: str, verbose: bool = False) -> pd.DataFrame:
    """Load settled donor results, filtered to the requested window."""
    all_results: list[pd.DataFrame] = []

    for source in DONOR_SOURCES:
        base = source.split("_")[0]
        files = sorted(glob.glob(str(LOCALDATA / f"{base}_*.csv.gz")))
        if not files:
            continue

        for f in files:
            path = Path(f)
            try:
                df = pd.read_csv(path, dtype=str)
            except Exception as exc:  # noqa: BLE001 - one bad cache file should not kill all donors
                if verbose:
                    print(f"  WARN: could not read donor file {path.name}: {exc}")
                continue

            required = {"date", "home", "away", "hs", "gs"}
            if not required.issubset(df.columns):
                continue

            df = df.copy()
            df["date"] = _normalise_date(df["date"])
            df = df[(df["date"] >= start) & (df["date"] <= end)].copy()
            if df.empty:
                continue

            df = df[df["hs"].notna() & df["gs"].notna()].copy()
            df = df[(df["hs"].astype(str) != "") & (df["gs"].astype(str) != "")].copy()
            if df.empty:
                continue

            df["hkey"] = _norm_key(df["home"])
            df["akey"] = _norm_key(df["away"])

            cols = ["date", "hkey", "akey", "hs", "gs"]
            if "ht_hs" in df.columns and "ht_gs" in df.columns:
                cols += ["ht_hs", "ht_gs"]
            all_results.append(df[cols])

    if not all_results:
        print("No donor data found for requested window.")
        sys.exit(1)

    combined = pd.concat(all_results, ignore_index=True)
    combined = combined.drop_duplicates(subset=["date", "hkey", "akey"], keep="first")
    return combined


def backfill_source(source_name: str, donor_df: pd.DataFrame, start: str, end: str) -> BackfillResult:
    files = sorted(glob.glob(str(LOCALDATA / f"{source_name}_*.csv.gz")))
    if not files:
        return BackfillResult(0, 0, {})

    updated_rows = 0
    file_counts: dict[str, int] = {}
    donor_has_ht_cols = "ht_hs" in donor_df.columns and "ht_gs" in donor_df.columns

    for f in files:
        path = Path(f)
        df = pd.read_csv(path, dtype=str)
        required = {"date", "home", "away", "hs", "gs"}
        if not required.issubset(df.columns):
            continue

        df = df.copy()
        df["date"] = _normalise_date(df["date"])
        in_window = (df["date"] >= start) & (df["date"] <= end)
        if not in_window.any():
            continue

        missing = df.loc[
            in_window
            & (
                df["hs"].isna()
                | (df["hs"].astype(str) == "")
                | df["gs"].isna()
                | (df["gs"].astype(str) == "")
            )
        ].copy()
        if missing.empty:
            continue

        missing = missing.reset_index(names="_row_index")
        missing["hkey"] = _norm_key(missing["home"])
        missing["akey"] = _norm_key(missing["away"])

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
        if (
            donor_has_ht_cols
            and "ht_hs" in df.columns
            and "ht_gs" in df.columns
            and "ht_hs_donor" in merged.columns
            and "ht_gs_donor" in merged.columns
        ):
            ht_mask = fill_mask & merged["ht_hs_donor"].notna()
            if ht_mask.any():
                merged.loc[ht_mask, "ht_hs"] = merged.loc[ht_mask, "ht_hs_donor"]
                merged.loc[ht_mask, "ht_gs"] = merged.loc[ht_mask, "ht_gs_donor"]
            update_cols += ["ht_hs", "ht_gs"]

        rows = merged.loc[fill_mask, "_row_index"]
        df.loc[rows, update_cols] = merged.loc[fill_mask, update_cols].values
        df.to_csv(path, index=False, compression="gzip")

        count = int(fill_mask.sum())
        updated_rows += count
        file_counts[path.name] = count

    return BackfillResult(updated_rows, len(file_counts), file_counts)


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
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-file update details. Default output is compact.",
    )
    args = parser.parse_args()

    start, end = resolve_window(args)

    print(f"Multi-source retrospective results backfill: {start} → {end}")
    print("=" * 65)

    donor_df = load_donor_results(start, end, verbose=args.verbose)
    print(f"Loaded {len(donor_df)} unique settled donor matches in window.\n")

    total_rows = 0
    total_files = 0
    by_source: dict[str, int] = {}
    verbose_file_counts: dict[str, dict[str, int]] = defaultdict(dict)

    for source in TARGET_SOURCES_WITH_RESULTS:
        result = backfill_source(source, donor_df, start, end)
        if result.updated_rows:
            by_source[source] = result.updated_rows
            verbose_file_counts[source] = result.file_counts
        total_rows += result.updated_rows
        total_files += result.updated_files

    if by_source:
        print("Updated rows by source:")
        for source, count in by_source.items():
            print(f"  {source}: {count}")
            if args.verbose:
                for filename, file_count in verbose_file_counts[source].items():
                    print(f"    {filename}: {file_count}")
    else:
        print("No missing scores filled; cache already settled for this window.")

    print(f"\nTotal rows updated: {total_rows} across {total_files} file(s)")
    print("Next: python3 scripts/build_warehouse.py")


if __name__ == "__main__":
    main()
