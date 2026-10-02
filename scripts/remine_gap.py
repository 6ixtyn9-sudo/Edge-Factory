#!/usr/bin/env python3
"""Run the approved, gap-only historical backfills.

This is the first B1 execution driver. It reads the committed B0 inventory and
never expands a date range into requests. The current approved order is:

    statarea gaps -> BetExplorer result gaps

Football-Data and Legalbet have separate bounded stages and are intentionally
not run by this command. There is no production/consensus update here.

Examples:
    PYTHONPATH=src python3 scripts/remine_gap.py --source statarea
    PYTHONPATH=src python3 scripts/remine_gap.py --source betexplorer_results
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.remine import merge_existing_wins, source_row_key  # noqa: E402

INVENTORY_PATH = LOCALDATA / "coverage_inventory.json"
AUDIT_PATH = LOCALDATA / f"remine_audit_{date.today().isoformat()}.jsonl"
CHALLENGE_MARKERS = (
    "captcha",
    "verify you are human",
    "checking your browser",
    "security verification",
    "access denied",
    "cf-chl-",
)


def load_inventory() -> dict:
    return json.loads(INVENTORY_PATH.read_text())


def sha256_bytes(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def append_audit(**fields: object) -> None:
    record = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        **fields,
    }
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with AUDIT_PATH.open("a") as fh:
        fh.write(json.dumps(record, sort_keys=True, ensure_ascii=False) + "\n")
    print("AUDIT " + json.dumps(record, sort_keys=True, ensure_ascii=False), flush=True)


def assert_public(body: str, url: str) -> None:
    lowered = body.lower()
    if any(marker in lowered for marker in CHALLENGE_MARKERS):
        raise RuntimeError(f"challenge detected at {url}")


def read_gzip(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with gzip.open(path, "rt", newline="", errors="replace") as fh:
        return list(csv.DictReader(fh))


def write_gzip(path: Path, rows: list[dict], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with gzip.open(tmp, "wt", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(path)


def import_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def accepted_incoming(source: str, existing: list[dict], incoming: list[dict], market: str) -> list[dict]:
    existing_keys = {source_row_key(source, row, market=market) for row in existing}
    seen = set(existing_keys)
    accepted: list[dict] = []
    for row in incoming:
        key = source_row_key(source, row, market=market)
        if key in seen:
            continue
        seen.add(key)
        accepted.append(row)
    return accepted


def run_statarea(inventory: dict) -> int:
    source = "statarea"
    dates = inventory["crawl_plan_inputs"][source]["proposed_internal_gap_days"]
    if not dates:
        print("statarea: inventory has no eligible gap days")
        return 0
    module = import_script("statarea_source", ROOT / "src/edgefactory/sources/statarea.py")
    columns = list(module.COLUMNS)
    committed = read_gzip(LOCALDATA / "statarea.csv.gz")
    accepted_total = 0
    for day in dates:
        url = f"https://old.statarea.com/predictions/{day}"
        try:
            rows = module.fetch_day(day)
            receipt = dict(getattr(module, "LAST_FETCH_RECEIPT", {}))
            status = receipt.get("status")
            if status in {403, 429}:
                raise RuntimeError(f"HTTP {status} at {url}")
            if status in {404, 410, "error"}:
                append_audit(source=source, date=day, url=url, status="crawl_failure", rows=0, **receipt)
                continue
            if not rows:
                append_audit(
                    source=source,
                    date=day,
                    url=url,
                    status="no_matches_day",
                    rows=0,
                    checksum=receipt.get("sha256"),
                    response_bytes=receipt.get("bytes"),
                    receipt=receipt,
                )
                continue
            accepted = accepted_incoming(source, committed, rows, "statarea")
            collision_count = len(rows) - len(accepted)
            hist_path = LOCALDATA / f"sa_hist_{day[:7]}.csv.gz"
            hist_existing = read_gzip(hist_path)
            hist_accepted = accepted_incoming(source, hist_existing, accepted, "statarea")
            if hist_accepted:
                write_gzip(hist_path, hist_existing + hist_accepted, columns)
            accepted_total += len(hist_accepted)
            append_audit(
                source=source,
                date=day,
                url=url,
                status="rows",
                rows=len(rows),
                accepted_rows=len(hist_accepted),
                collision_rows=collision_count,
                checksum=receipt.get("sha256"),
                response_bytes=receipt.get("bytes"),
                receipt=receipt,
            )
        except Exception as exc:
            # 403/challenge is a hard stop; transport/layout failures are not
            # converted into no_matches_day.
            append_audit(source=source, date=day, url=url, status="crawl_failure", rows=0, checksum=None, checksum_status="unavailable_no_response_bytes", response_bytes=None, error=str(exc))
            if "403" in str(exc) or "429" in str(exc) or "challenge" in str(exc).lower():
                raise
    print(f"statarea: accepted {accepted_total} rows into sa_hist; committed ledger unchanged")
    return accepted_total


def _betexplorer_module():
    return import_script("backfill_betexplorer", ROOT / "scripts/backfill_betexplorer.py")


def run_betexplorer_results(inventory: dict) -> int:
    source = "betexplorer_results"
    days = inventory["crawl_plan_inputs"][source]["proposed_internal_gap_days"]
    if not days:
        print("betexplorer_results: inventory has no eligible gap days")
        return 0
    module = _betexplorer_module()
    columns = list(module.RESULT_COLUMNS)
    existing_by_month: dict[str, list[dict]] = {}
    for path in sorted(LOCALDATA.glob("betexplorer_results_*.csv.gz")):
        month = path.name.removeprefix("betexplorer_results_").split(".", 1)[0]
        existing_by_month[month] = read_gzip(path)

    rate_limits = 0

    def on_429() -> None:
        nonlocal rate_limits
        rate_limits += 1
        if rate_limits >= 2:
            raise module.RateLimitCluster("BetExplorer 429 cluster; aborting approved backfill")

    accepted_total = 0
    for day in days:
        year, month, dom = day.split("-")
        url = f"{module.BASE}/football/results/?year={year}&month={month}&day={dom}"
        try:
            body = module.fetch(url, sleep=1.0, jitter=0.25, on_429=on_429)
            body_bytes = body.encode("utf-8")
            assert_public(body, url)
            rows = module.parse_results_page(body)
            rows = [row for row in rows if row.get("date") == day]
            if not rows:
                append_audit(
                    source=source,
                    date=day,
                    url=url,
                    status="no_matches_day",
                    rows=0,
                    checksum=sha256_bytes(body_bytes),
                    response_bytes=len(body_bytes),
                    rate_limit_count=rate_limits,
                )
                continue
            month_key = day[:7]
            path = LOCALDATA / f"betexplorer_results_{month_key}.csv.gz"
            existing = existing_by_month.setdefault(month_key, read_gzip(path))
            accepted = accepted_incoming(source, existing, rows, "settled_score")
            merged, merge_audit = merge_existing_wins(
                source,
                existing,
                accepted,
                key_fn=lambda src, row: source_row_key(src, row, market="settled_score"),
            )
            if accepted:
                write_gzip(path, merged, columns)
            existing_by_month[month_key] = merged
            accepted_total += len(accepted)
            append_audit(
                source=source,
                date=day,
                url=url,
                status="rows",
                rows=len(rows),
                accepted_rows=len(accepted),
                collision_rows=merge_audit["incoming_collision_rows_skipped"],
                checksum=sha256_bytes(body_bytes),
                response_bytes=len(body_bytes),
                rate_limit_count=rate_limits,
            )
        except module.RateLimitCluster:
            append_audit(source=source, date=day, url=url, status="aborted_429_cluster", rows=0)
            raise
        except Exception as exc:
            append_audit(source=source, date=day, url=url, status="crawl_failure", rows=0, checksum=None, checksum_status="unavailable_no_response_bytes", response_bytes=None, error=str(exc))
            if "403" in str(exc) or "429" in str(exc) or "challenge" in str(exc).lower():
                raise
    print(f"betexplorer_results: accepted {accepted_total} rows; result cache only")
    return accepted_total


def main() -> None:
    global INVENTORY_PATH
    parser = argparse.ArgumentParser(description="Run approved gap-only historical result backfills")
    parser.add_argument("--source", choices=("statarea", "betexplorer_results", "all"), default="all")
    parser.add_argument("--inventory", type=Path, default=INVENTORY_PATH)
    args = parser.parse_args()
    INVENTORY_PATH = args.inventory
    inventory = load_inventory()
    if args.source in {"statarea", "all"}:
        run_statarea(inventory)
    if args.source in {"betexplorer_results", "all"}:
        run_betexplorer_results(inventory)


if __name__ == "__main__":
    main()
