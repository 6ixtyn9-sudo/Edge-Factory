#!/usr/bin/env python3
"""Build a deterministic, local-only coverage inventory for re-mining.

B0 is deliberately read-only with respect to the network and source data. It
reads committed/cache CSV or CSV.GZ files, records the exact date coverage and
internal gaps, and emits the inventory that a later gap-aware crawl driver must
consume. It never opens a URL and never mutates a source ledger or warehouse.

Usage:
    PYTHONPATH=src python3 scripts/coverage_inventory.py \
        --observed-at 2026-10-02T00:00:00Z \
        --output localdata/coverage_inventory.json \
        --append-plan docs/operator/REMINE-PLAN.nd
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
LOCALDATA = ROOT / "localdata"
sys.path.insert(0, str(ROOT / "src"))

from edgefactory.identity import source_team_key  # noqa: E402


# The source list is intentionally explicit. A missing source is an inventory
# fact, not permission to invent a crawl range. ``warehouse_tables`` describes
# the table names the existing warehouse builder would materialize when the
# corresponding source capture exists.
SOURCE_SPECS: dict[str, dict] = {
    "statarea": {
        "patterns": ["statarea*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["statarea", "statarea_settled"],
        "market_groups": {
            "1x2_probability": ("p1", "px", "p2"),
            "ht_1x2_probability": ("p1_ht", "px_ht", "p2_ht"),
            "ou_probability": ("p_o15", "p_o25", "p_o35"),
        },
    },
    "zulubet": {
        "patterns": ["zulubet*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["zulubet", "zulubet_settled"],
        "market_groups": {
            "1x2_probability": ("p1", "px", "p2"),
            "1x2_odds": ("odd1", "oddx", "odd2"),
        },
    },
    "predictz": {
        "patterns": ["predictz*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["predictz_raw", "predictz_settled"],
        "market_groups": {
            "1x2_pick": ("pick",),
            "1x2_odds": ("odd1", "oddx", "odd2"),
        },
    },
    "windrawwin": {
        "patterns": ["windrawwin*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["windrawwin"],
        "market_groups": {"1x2_pick": ("pick",)},
    },
    "bettingclosed": {
        "patterns": ["bettingclosed*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["bettingclosed", "bettingclosed_settled"],
        "market_groups": {
            "1x2": ("pick_1x2", "odd_pick_1x2"),
            "ou_2.5": ("pick_ou", "odd_pick_ou"),
            "btts": ("pick_btts", "odd_pick_btts"),
            "1x2_odds": ("odd1", "oddx", "odd2"),
        },
    },
    "betexplorer_odds": {
        "patterns": ["betexplorer_odds_*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["betexplorer", "betexplorer_settled"],
        "market_groups": {
            "1x2_odds": ("odd1", "oddx", "odd2"),
            "1x2_bookmaker_rows": ("n_odd1", "n_oddx", "n_odd2"),
        },
    },
    "betexplorer_results": {
        "patterns": ["betexplorer_results_*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["betexplorer", "betexplorer_settled"],
        "market_groups": {"settled_score": ("hs", "gs")},
    },
    "scoutingstats": {
        "patterns": ["scoutingstats*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["scoutingstats", "scoutingstats_settled"],
        "market_groups": {
            "1x2_probability": ("p1", "px", "p2"),
            "ou_probability": ("p_o15", "p_o25", "p_o35"),
            "btts_probability": ("p_gg", "p_ng"),
            "1x2_odds": ("odd1", "oddx", "odd2"),
        },
    },
    "prosoccer": {
        "patterns": ["prosoccer*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["prosoccer", "prosoccer_settled"],
        "market_groups": {
            "1x2_probability": ("p1", "px", "p2"),
            "ou_2.5_probability": ("p_u25", "p_o25"),
            "1x2_odds": ("odd1", "oddx", "odd2"),
        },
    },
    "afootballreport": {
        "patterns": ["afootballreport*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["afootballreport"],
        "market_groups": {"declared_market": ("market", "tip")},
    },
    "betclan": {
        "patterns": ["betclan*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["betclan"],
        "market_groups": {"1x2_probability": ("p1", "px", "p2")},
    },
    "freesupertips": {
        "patterns": ["freesupertips*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["freesupertips"],
        "market_groups": {"tipster_market": ("tip", "odds", "confidence")},
    },
    "forebet": {
        "patterns": ["forebet*.csv.gz"],
        "date_fields": ["date"],
        "warehouse_tables": ["forebet", "forebet_settled"],
        "market_groups": {
            "1x2_probability": ("p1", "px", "p2"),
            "1x2_odds": ("odd1", "oddx", "odd2"),
            "ou_probability": ("p_under", "p_over"),
            "ou_odds": ("odd_under", "odd_over"),
            "btts_probability": ("p_gg", "p_ng"),
            "btts_odds": ("odd_gg", "odd_ng"),
            "ht_1x2_probability": ("p1_ht", "px_ht", "p2_ht"),
        },
    },
}

# Auxiliary caches are reported separately so the operator can see that the
# ``sa``/``fb`` aliases are the same held ledgers rather than extra sources.
CACHE_SPECS: dict[str, dict] = {
    "sa_cache": {"patterns": ["statarea*.csv.gz"], "alias_of": "statarea", "date_fields": ["date"]},
    "fb_cache": {"patterns": ["forebet*.csv.gz"], "alias_of": "forebet", "date_fields": ["date"]},
    "clv_cache": {"patterns": ["clv_snapshots_*.csv.gz"], "alias_of": "clv_snapshots", "date_fields": ["match_date"]},
}


def _tracked_files() -> set[str]:
    try:
        out = subprocess.check_output(
            ["git", "ls-files", "--", "localdata"], cwd=ROOT, text=True
        )
    except (OSError, subprocess.CalledProcessError):
        return set()
    return {line.strip() for line in out.splitlines() if line.strip()}


def _files(patterns: Iterable[str]) -> list[Path]:
    result: set[Path] = set()
    for pattern in patterns:
        result.update(LOCALDATA.glob(pattern))
    return sorted(p for p in result if p.is_file())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _nonempty(row: dict, field: str) -> bool:
    value = row.get(field)
    return value is not None and str(value).strip() != ""


def _date_value(row: dict, fields: Iterable[str]) -> str | None:
    for field in fields:
        raw = str(row.get(field) or "").strip()
        if len(raw) >= 10:
            candidate = raw[:10]
            try:
                date.fromisoformat(candidate)
                return candidate
            except ValueError:
                continue
    return None


def _market_labels(row: dict, spec: dict) -> list[str]:
    labels: list[str] = []
    for label, fields in spec.get("market_groups", {}).items():
        if any(_nonempty(row, field) for field in fields):
            labels.append(label)
    raw_market = str(row.get("market") or "").strip()
    if raw_market:
        labels.append(f"declared:{raw_market}")
    return sorted(set(labels))


def _fixture_key(source: str, row: dict, day: str | None, market: str) -> str | None:
    if not day:
        return None
    home = row.get("home") or row.get("home_team")
    away = row.get("away") or row.get("away_team")
    if home and away:
        fixture = f"{source_team_key(home)}::{source_team_key(away)}"
    elif row.get("event_id"):
        fixture = f"event:{str(row['event_id']).strip()}"
    elif row.get("match_id"):
        fixture = f"match:{str(row['match_id']).strip()}"
    else:
        return None
    return f"{source}|{day}|{fixture}|{market}"


def _empty_date_summary() -> dict:
    return {
        "min": None,
        "max": None,
        "observed_days": 0,
        "missing_internal_days": [],
        "missing_internal_day_count": 0,
        "invalid_date_rows": 0,
    }


def _date_summary(days: set[str], invalid: int) -> dict:
    result = _empty_date_summary()
    result["invalid_date_rows"] = invalid
    if not days:
        return result
    ordered = sorted(days)
    result["min"], result["max"] = ordered[0], ordered[-1]
    result["observed_days"] = len(ordered)
    present = set(ordered)
    cursor, end = date.fromisoformat(ordered[0]), date.fromisoformat(ordered[-1])
    gaps: list[str] = []
    while cursor <= end:
        iso = cursor.isoformat()
        if iso not in present:
            gaps.append(iso)
        cursor += timedelta(days=1)
    result["missing_internal_days"] = gaps
    result["missing_internal_day_count"] = len(gaps)
    return result


def _warehouse_snapshot(expected: set[str]) -> dict:
    db_path = LOCALDATA / "warehouse.duckdb"
    snapshot = {
        "path": str(db_path.relative_to(ROOT)),
        "present": db_path.exists(),
        "tables": {},
    }
    if not db_path.exists():
        snapshot["tables"] = {name: {"status": "missing"} for name in sorted(expected)}
        return snapshot
    try:
        import duckdb

        con = duckdb.connect(str(db_path), read_only=True)
        names = {row[0] for row in con.execute("SHOW TABLES").fetchall()}
        for name in sorted(expected):
            if name not in names:
                snapshot["tables"][name] = {"status": "missing"}
                continue
            count = int(con.execute(f"SELECT count(*) FROM {name}").fetchone()[0])
            snapshot["tables"][name] = {"status": "present", "rows": count}
        con.close()
    except Exception as exc:  # inventory must still report raw-file coverage
        snapshot["error"] = f"{type(exc).__name__}: {exc}"
        snapshot["tables"] = {name: {"status": "unreadable"} for name in sorted(expected)}
    return snapshot


def inventory_one(name: str, spec: dict, tracked: set[str]) -> dict:
    paths = _files(spec["patterns"])
    daily: Counter[str] = Counter()
    markets: Counter[str] = Counter()
    market_days: dict[str, set[str]] = defaultdict(set)
    days: set[str] = set()
    invalid_dates = 0
    total_rows = committed_rows = cache_rows = 0
    key_counts: Counter[str] = Counter()
    key_examples: dict[str, dict] = {}
    file_records: list[dict] = []

    for path in paths:
        rel = str(path.relative_to(ROOT))
        committed = rel in tracked
        file_rows = 0
        file_days: set[str] = set()
        with gzip.open(path, "rt", newline="", errors="replace") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                file_rows += 1
                total_rows += 1
                if committed:
                    committed_rows += 1
                else:
                    cache_rows += 1
                day = _date_value(row, spec.get("date_fields", ["date"]))
                if not day:
                    invalid_dates += 1
                    continue
                days.add(day)
                file_days.add(day)
                daily[day] += 1
                labels = _market_labels(row, spec)
                for label in labels:
                    markets[label] += 1
                    market_days[label].add(day)
                # A row with several market columns is represented by one
                # combined market key. Sources with one explicit market use
                # that value; this prevents one physical row becoming a false
                # duplicate merely because it contains several columns.
                market_key = "|".join(labels) if labels else "row"
                key = _fixture_key(name, row, day, market_key)
                if key:
                    key_counts[key] += 1
                    key_examples.setdefault(
                        key,
                        {
                            "date": day,
                            "home": row.get("home") or row.get("home_team"),
                            "away": row.get("away") or row.get("away_team"),
                            "market": market_key,
                        },
                    )
        file_records.append(
            {
                "path": rel,
                "status": "committed" if committed else "cache-only",
                "rows": file_rows,
                "date_min": min(file_days) if file_days else None,
                "date_max": max(file_days) if file_days else None,
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )

    duplicate_groups = {key: count for key, count in key_counts.items() if count > 1}
    duplicate_rows = sum(count - 1 for count in duplicate_groups.values())
    duplicate_examples = []
    for key, count in sorted(duplicate_groups.items(), key=lambda item: (-item[1], item[0]))[:20]:
        example = dict(key_examples[key])
        example.update({"key": key, "rows": count})
        duplicate_examples.append(example)

    date_info = _date_summary(days, invalid_dates)
    return {
        "status": "committed" if committed_rows else ("cache-only" if cache_rows else "absent"),
        "files": file_records,
        "rows": total_rows,
        "committed_rows": committed_rows,
        "cache_only_rows": cache_rows,
        "date_range": date_info,
        "per_day_row_counts": dict(sorted(daily.items())),
        "markets": {
            label: {
                "rows": count,
                "observed_days": len(market_days[label]),
                "date_min": min(market_days[label]) if market_days[label] else None,
                "date_max": max(market_days[label]) if market_days[label] else None,
            }
            for label, count in sorted(markets.items())
        },
        "duplicate_keys": {
            "definition": "source|date|source_team_key(home)::source_team_key(away)|market; event_id/match_id fallback when teams are absent",
            "normalizer": "edgefactory.identity.source_team_key",
            "unique_key_count": len(key_counts),
            "duplicate_group_count": len(duplicate_groups),
            "duplicate_row_count": duplicate_rows,
            "examples": duplicate_examples,
        },
        "warehouse_tables": spec.get("warehouse_tables", []),
        "crawl_plan": {
            "driver_input": "date_range.missing_internal_days",
            "proposed_internal_gap_days": date_info["missing_internal_days"],
            "proposed_internal_gap_count": date_info["missing_internal_day_count"],
            "boundary_probe_below_floor": bool(days),
            "operator_approval_required": True,
        },
    }


def inventory_cache(name: str, spec: dict, tracked: set[str]) -> dict:
    # Cache records intentionally omit market/key analysis because they are
    # observability inputs rather than source ledgers; the source row carries
    # the canonical counts. CLV still receives its exact date coverage.
    paths = _files(spec["patterns"])
    daily: Counter[str] = Counter()
    days: set[str] = set()
    rows = committed = cache = 0
    files = []
    for path in paths:
        rel = str(path.relative_to(ROOT))
        is_committed = rel in tracked
        file_rows = 0
        with gzip.open(path, "rt", newline="", errors="replace") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                file_rows += 1
                rows += 1
                committed += int(is_committed)
                cache += int(not is_committed)
                day = _date_value(row, spec.get("date_fields", ["date"]))
                if day:
                    days.add(day)
                    daily[day] += 1
        files.append({
            "path": rel,
            "status": "committed" if is_committed else "cache-only",
            "rows": file_rows,
            "sha256": _sha256(path),
            "bytes": path.stat().st_size,
        })
    date_info = _date_summary(days, 0)
    return {
        "status": "committed" if committed else ("cache-only" if cache else "absent"),
        "alias_of": spec.get("alias_of"),
        "files": files,
        "rows": rows,
        "committed_rows": committed,
        "cache_only_rows": cache,
        "date_range": date_info,
        "per_day_row_counts": dict(sorted(daily.items())),
        "crawl_plan": {
            "driver_input": "date_range.missing_internal_days",
            "proposed_internal_gap_days": date_info["missing_internal_days"],
            "proposed_internal_gap_count": date_info["missing_internal_day_count"],
            "operator_approval_required": True,
        },
    }


def _market_text(data: dict) -> str:
    return ", ".join(
        f"{label} ({info['rows']:,} rows/{info['observed_days']}d)"
        for label, info in data.get("markets", {}).items()
    ) or "—"


def _gap_text(data: dict) -> str:
    gaps = data.get("date_range", {}).get("missing_internal_days", [])
    if not gaps:
        return "0"
    head = ", ".join(gaps[:5])
    return f"{len(gaps)} ({head}{', …' if len(gaps) > 5 else ''})"


def _plan_rows(inventory: dict) -> list[str]:
    rows = []
    for name, data in inventory["sources"].items():
        availability = data.get("status", "absent")
        committed = data.get("committed_rows", 0)
        cache = data.get("cache_only_rows", 0)
        date_info = data.get("date_range", {})
        date_range_text = (
            f"{date_info.get('min')} → {date_info.get('max')}"
            if date_info.get("min") else "—"
        )
        warehouse = ", ".join(
            f"{table}:{inventory['warehouse']['tables'].get(table, {}).get('status', 'unknown')}"
            for table in data.get("warehouse_tables", [])
        ) or "—"
        rows.append(
            "| {name} | {availability} | {committed:,} / {cache:,} / {total:,} | "
            "{date_range} ({days}d) | {gaps} | {markets} | {dupes} groups, {dup_rows} rows | {warehouse} |".format(
                name=name,
                availability=availability,
                committed=committed,
                cache=cache,
                total=data.get("rows", 0),
                date_range=date_range_text,
                days=date_info.get("observed_days", 0),
                gaps=_gap_text(data),
                markets=_market_text(data),
                dupes=data.get("duplicate_keys", {}).get("duplicate_group_count", 0),
                dup_rows=data.get("duplicate_keys", {}).get("duplicate_row_count", 0),
                warehouse=warehouse,
            )
        )
    for name, data in inventory["caches"].items():
        date_info = data.get("date_range", {})
        date_range_text = (
            f"{date_info.get('min')} → {date_info.get('max')}"
            if date_info.get("min") else "—"
        )
        rows.append(
            f"| {name} | {data.get('status')} (alias/cache) | "
            f"{data.get('committed_rows', 0):,} / {data.get('cache_only_rows', 0):,} / {data.get('rows', 0):,} | "
            f"{date_range_text} ({date_info.get('observed_days', 0)}d) | {_gap_text(data)} | — | — | alias of {data.get('alias_of', 'cache')} |"
        )
    return rows


def append_plan(path: Path, inventory: dict) -> None:
    marker_start = "<!-- coverage-inventory:start -->"
    marker_end = "<!-- coverage-inventory:end -->"
    table = "\n".join([
        marker_start,
        "## B0 coverage inventory (local-only, no network)",
        "",
        f"Observed: `{inventory['observed_at']}`. The inventory is the only input to a future gap-aware crawl plan; no crawl budget is approved by this artifact.",
        "",
        "| source | availability | committed / cache-only / total rows | date range (observed days) | internal gaps (crawl candidates) | market coverage | duplicate keys | warehouse tables |",
        "|---|---|---:|---|---|---|---|---|",
        *_plan_rows(inventory),
        "",
        "**Key rule:** `source + date + source_team_key(home) + source_team_key(away) + market`; existing committed rows win collisions. `source_team_key` is the existing alias-aware normalization seam. The `proposed_internal_gap_days` arrays in `localdata/coverage_inventory.json` are the driver input; ranges are display-only.",
        "",
        "**Budget gate:** proposed counts above are internal missing days only. Empty sources have no crawl range and require an operator-approved boundary/date floor. ZuluBet robots policy and the first Football-Data CSV download remain separately blocked pending operator approval.",
        marker_end,
    ]) + "\n"
    existing = path.read_text() if path.exists() else "# Re-mining plan\n\n"
    if marker_start in existing and marker_end in existing:
        before = existing.split(marker_start, 1)[0]
        after = existing.split(marker_end, 1)[1].lstrip("\n")
        suffix = ("\n" + after) if after else ""
        path.write_text(before + table + suffix)
    else:
        separator = "\n" if existing.endswith("\n") else "\n\n"
        path.write_text(existing + separator + table)


def build_inventory(observed_at: str) -> dict:
    tracked = _tracked_files()
    expected_tables = {
        table
        for spec in SOURCE_SPECS.values()
        for table in spec.get("warehouse_tables", [])
    }
    sources = {
        name: inventory_one(name, spec, tracked)
        for name, spec in SOURCE_SPECS.items()
    }
    caches = {
        name: inventory_cache(name, spec, tracked)
        for name, spec in CACHE_SPECS.items()
    }
    return {
        "schema_version": "coverage_inventory.v1",
        "observed_at": observed_at,
        "read_only": True,
        "network_access": False,
        "source_files_are_immutable_inputs": True,
        "normalization": {
            "fixture_key": "source|date|source_team_key(home)::source_team_key(away)|market",
            "team_normalizer": "edgefactory.identity.source_team_key",
            "market_note": "one physical row's populated market fields are combined into one market key for duplicate auditing",
        },
        "sources": sources,
        "caches": caches,
        "warehouse": _warehouse_snapshot(expected_tables),
        "crawl_plan_inputs": {
            name: data.get("crawl_plan", {}) for name, data in sources.items()
        },
        "gates": {
            "zulubet_robots_policy": "operator approval required",
            "football_data_first_csv": "operator approval required",
            "production_champion_weight": "zero",
            "network_crawl": "not run in B0",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate local-only source coverage inventory")
    parser.add_argument("--observed-at", default="2026-10-02T00:00:00Z")
    parser.add_argument("--output", type=Path, default=LOCALDATA / "coverage_inventory.json")
    parser.add_argument("--append-plan", type=Path, default=None)
    args = parser.parse_args()

    inventory = build_inventory(args.observed_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(inventory, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    if args.append_plan:
        args.append_plan.parent.mkdir(parents=True, exist_ok=True)
        append_plan(args.append_plan, inventory)

    print("# B0 local coverage inventory — no network")
    print("| source | status | rows | date range | internal gap days | proposed crawl days |")
    print("|---|---|---:|---|---:|---:|")
    for name, data in inventory["sources"].items():
        dates = data["date_range"]
        print(
            f"| {name} | {data['status']} | {data['rows']:,} | "
            f"{dates['min'] or '—'} → {dates['max'] or '—'} | "
            f"{dates['missing_internal_day_count']} | "
            f"{data['crawl_plan']['proposed_internal_gap_count']} |"
        )
    def display_path(path: Path) -> str:
        resolved = path if path.is_absolute() else ROOT / path
        try:
            return str(resolved.relative_to(ROOT))
        except ValueError:
            return str(resolved)

    print(f"\nWrote {display_path(args.output)}")
    if args.append_plan:
        print(f"Updated {display_path(args.append_plan)}")


if __name__ == "__main__":
    main()
